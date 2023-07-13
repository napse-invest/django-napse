from django.db.utils import IntegrityError

from django_napse.core.models import Exchange, ExchangeAccount, NapseSpace
from django_napse.utils.model_test_case import ModelTestCase


class NapseSpaceTestCase(ModelTestCase):
    model = NapseSpace

    def simple_create(self):
        return NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")

    def setUp(self):
        self.exchange = Exchange.objects.create(
            name="random exchange",
            description="random description",
        )
        self.exchange_account = ExchangeAccount.objects.create(
            exchange=self.exchange,
            testing=True,
            name="random exchange account 1",
            description="random description",
        )

    def test_create_napse_space_with_same_name(self):
        NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")
        NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")

    def test_create_napse_space_with_same_name_and_identifier(self):
        first_space = NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")
        second_space = NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")
        second_space.identifier = first_space.identifier

        with self.assertRaises(IntegrityError):
            second_space.save()
