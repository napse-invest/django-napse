from django_napse.utils.serializers.fields import Field, IntField, StrField, BoolField, DatetimeField, MethodField, UUIDField
from django_napse.utils.serializers.serializer import Serializer, MetaSerializer

from django_napse.core.models import Exchange, ExchangeAccount
from django.test import TestCase
from rest_framework.serializers import ValidationError

"""
python tests/test_app/manage.py test tests.django_tests.test_serializer -v2 --keepdb --parallel
"""


class ExchangeSerializer(Serializer):
    Model = Exchange
    name = StrField(required=True)
    description = StrField()
    test_int_field = IntField()


class ExchangeAccountSerializer(Serializer):
    Model = ExchangeAccount
    uuid = UUIDField()
    exchange = ExchangeSerializer(required=True)
    name = StrField(required=True)
    testing = BoolField(required=True)
    description = StrField()
    default = BoolField()
    created_at = DatetimeField()
    tickers = MethodField()

    def get_tickers(self, instance):
        return instance.exchange.get_tickers()

    def validate_data(self, data):
        data["testing"] = True
        return super().validate_data(data)


class SerializerSerializationTestCase(TestCase):
    def setUp(self):
        self.exchange = Exchange.objects.create(name="Binance", description="Binance exchange")
        self.exchange_account = ExchangeAccount.objects.create(
            exchange=self.exchange,
            name="Binance Account",
            testing=True,
            description="Binance account description",
            default=True,
        )

    def test_exchange_serialization(self):
        self.exchange.test_int_field = 1  # Just for testing the int field
        exchange_serializer = ExchangeSerializer(instance=self.exchange)
        data = exchange_serializer.data
        self.assertEqual(
            data,
            {
                "name": "Binance",
                "description": "Binance exchange",
                "test_int_field": 1,
            },
        )

    def test_exchange_account_serialization(self):
        exchange_account_serializer = ExchangeAccountSerializer(self.exchange_account)
        data = exchange_account_serializer.data
        self.assertEqual(
            data,
            {
                "uuid": str(self.exchange_account.uuid),
                "exchange": {"name": "Binance", "description": "Binance exchange"},
                "name": "Binance Account",
                "testing": True,
                "description": "Binance account description",
                "default": True,
                "created_at": self.exchange_account.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "tickers": [],
            },
        )

    def test_many_serialization(self):
        instances = [self.exchange for _ in range(10)]
        exchange_serializer = ExchangeSerializer(many=True, instance=instances)
        data = exchange_serializer.data
        self.assertEqual(len(data), 10)

    def test_source_serialization(self):
        exchange_account_serializer = ExchangeAccountSerializer
        exchange_account_serializer._fields["exchange"] = StrField(source="exchange.name")
        exchange_account_serializer._compiled_fields = MetaSerializer._compile_fields(
            fields=exchange_account_serializer._fields,
            serializer_cls=exchange_account_serializer,
        )

        exchange_account_serializer = exchange_account_serializer(self.exchange_account)
        data = exchange_account_serializer.data
        print(data)
        self.assertEqual(data.get("exchange"), self.exchange.name)

        # reset
        exchange_account_serializer = ExchangeAccountSerializer
        exchange_account_serializer._fields["exchange"] = ExchangeSerializer()
        exchange_account_serializer._compiled_fields = MetaSerializer._compile_fields(
            fields=exchange_account_serializer._fields,
            serializer_cls=exchange_account_serializer,
        )

    def test_serialization_with_missing_required_field(self):
        exchange_account_serializer = ExchangeAccountSerializer()
        exchange_account_serializer._fields["required_field"] = Field(required=True)
        exchange_account_serializer._compiled_fields = MetaSerializer._compile_fields(
            fields=exchange_account_serializer._fields,
            serializer_cls=exchange_account_serializer.__class__,
        )

        with self.assertRaises(ValueError):
            exchange_account_serializer.data  # noqa: B018

        # reset
        exchange_account_serializer = ExchangeAccountSerializer
        exchange_account_serializer._fields.pop("required_field")
        exchange_account_serializer._compiled_fields = MetaSerializer._compile_fields(
            fields=exchange_account_serializer._fields,
            serializer_cls=exchange_account_serializer,
        )


class SerializerValidationTestCase(TestCase):
    def setUp(self):
        self.exchange = Exchange.objects.create(name="Binance", description="Binance exchange")
        self.exchange_account = ExchangeAccount.objects.create(
            exchange=self.exchange,
            name="Binance Account",
            testing=True,
            description="Binance account description",
            default=True,
        )

    def test_exchange_validation_and_creation(self):
        data = {"name": "TEST", "description": "Test exchange"}
        exchange_serializer = ExchangeSerializer(data=data)
        instance = exchange_serializer.create()
        self.assertEqual(isinstance(instance, Exchange), True)
        self.assertEqual(exchange_serializer.data, data)

    def test_exchange_account_validation_and_creation(self):
        data = {
            "name": "TEST exchange account",
            "description": "Test exchange",
            "exchange": self.exchange.id,
            "testing": True,
        }
        exchange_serializer = ExchangeAccountSerializer(data=data)
        instance = exchange_serializer.create()
        self.assertEqual(isinstance(instance, ExchangeAccount), True)

    def test_exchange_validation_and_update(self):
        data = {"name": "TEST", "description": "new description"}
        exchange_serializer = ExchangeSerializer(data=data)
        instance = exchange_serializer.update(instance=self.exchange)
        self.assertEqual(isinstance(instance, Exchange), True)
        self.assertEqual(instance.description, "new description")

    def test_validation_with_missing_required_field(self):
        with self.assertRaises(ValidationError):
            exchange_serializer = ExchangeSerializer(data={"description": "Test exchange"})  # noqa: F841

    def test_validation_with_invalid_field(self):
        data = {
            "name": "TEST exchange account",
            "description": "Test exchange",
            "exchange": {"name": 12},
            "testing": True,
        }
        with self.assertRaises(ValidationError):
            ExchangeAccountSerializer(data=data)

        data = {
            "name": "TEST",
            "description": "Test exchange",
            "test_int_field": "whatever",
        }
        with self.assertRaises(ValidationError):
            ExchangeSerializer(data=data)
        # with self.assertRaises(ValidationError):
        #     ExchangeAccountSerializer(data=data)
        # eas = ExchangeAccountSerializer(data=data)
        # from pprint import pprint

        # pprint(eas.validated_data)
        # pprint(eas._validators)

    def test_validation_with_invalid_data(self):
        data = 1
        with self.assertRaises(ValidationError):
            ExchangeSerializer(data=data)

    def test_validation_overwrite(self):
        data = {
            "name": "TEST exchange account",
            "description": "Test exchange",
            "exchange": self.exchange.id,
            "testing": False,
        }
        exchange_serializer = ExchangeAccountSerializer(data=data)
        instance = exchange_serializer.create()
        self.assertEqual(isinstance(instance, ExchangeAccount), True)
        self.assertEqual(
            exchange_serializer.validated_data,
            {
                "name": "TEST exchange account",
                "description": "Test exchange",
                "exchange": self.exchange,
                "testing": True,
            },
        )

    def test_get_validated_data_before_validation(self):
        exchange_serializer = ExchangeSerializer()
        with self.assertRaises(ValueError):
            exchange_serializer.validated_data  # noqa: B018

    def test_model_action_before_validation(self):
        exchange_serializer = ExchangeSerializer()
        with self.assertRaises(ValueError):
            exchange_serializer.create()

    def test_model_action_without_model(self):
        exchange_serializer = ExchangeSerializer()
        exchange_serializer.Model = None
        with self.assertRaises(ValueError):
            exchange_serializer.create({})

    def _test_perf(self):
        instances = [self.exchange_account for _ in range(1_000_000)]
        from time import time

        start = time()
        serializer = ExchangeAccountSerializer(instance=instances, many=True)
        print(f"setup: {time() - start:0.3f}s")
        data = serializer.data
        print(f"Total time{time() - start:0.6f}s")
        self.assertEqual(len(data), 1_000_000)
