from django.db.utils import IntegrityError

from django_napse.core.models import Currency, Exchange, ExchangeAccount, NapseSpace, SpaceWallet
from django_napse.utils.model_test_case import ModelTestCase


class CurrencyTestCase(ModelTestCase):
    model = Currency

    def setUp(self) -> None:
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
        self.space = NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")
        self.wallet = SpaceWallet.objects.create(title="Test Wallet", owner=self.space)

    def simple_create(self):
        return Currency.objects.create(wallet=self.wallet, ticker="BTC", amount=1, mbp=20000)

    def test_create_currency(self):
        Currency.objects.create(wallet=self.wallet, ticker="BTC", amount=1, mbp=20000)

    def test_duplicate_currency_for_a_wallet(self):
        Currency.objects.create(wallet=self.wallet, ticker="BTC", amount=1, mbp=20000)
        with self.assertRaises(IntegrityError):
            Currency.objects.create(wallet=self.wallet, ticker="BTC", amount=1, mbp=20000)

    def test_property_testing(self):
        currency = Currency.objects.create(wallet=self.wallet, ticker="BTC", amount=1, mbp=20000)
        self.assertTrue(currency.testing)
