from django.db.utils import IntegrityError

from django_napse.core.models import Currency
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.wallets.test_currency -v2 --keepdb --parallel
"""


class CurrencyTestCase:
    model = Currency

    def setUp(self) -> None:
        self.wallet = self.space.wallet

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


class CurrencyBINANCETestCase(CurrencyTestCase, ModelTestCase):
    exchange = "BINANCE"
