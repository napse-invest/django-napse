from django_napse.utils.serializers.fields import Field, IntField, StrField, BoolField, DatetimeField, MethodField, UUIDField
from django_napse.utils.serializers.serializer import Serializer

from django_napse.core.models import Exchange, ExchangeAccount
from django_napse.utils.custom_test_case import CustomTestCase
from django.test import TestCase

"""
python tests/test_app/manage.py test tests.django_tests.test_serializer -v2 --keepdb --parallel
"""


class ExchangeSerializer(Serializer):
    name = StrField()
    description = StrField()
    test_int_field = IntField()


class ExchangeAccountSerializer(Serializer):
    uuid = UUIDField()
    exchange = ExchangeSerializer()
    name = StrField()
    testing = BoolField()
    description = StrField()
    default = BoolField()
    created_at = DatetimeField()
    tickers = MethodField()

    def get_tickers(self, instance):
        return instance.exchange.get_tickers()


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

    def test_exchange_validation(self):
        pass

    def test_exchange_account_validation(self):
        pass


class SerializerValidationTestCase(TestCase):
    pass
