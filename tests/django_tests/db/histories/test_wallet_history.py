from django_napse.core.models.histories.wallet import WalletHistory
from django_napse.core.models.wallets.currency import Currency
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.db.histories.test_wallet_history -v2 --keepdb --parallel
"""


class WalletHistoryTestCase:
    model = WalletHistory

    def simple_create(self):
        wallet = self.space.wallet
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        Currency.objects.create(wallet=wallet, ticker="ETH", amount=0, mbp=1000)
        return wallet.history

    def test_generate_data_points(self):
        history = self.simple_create()
        history.generate_data_point()


class WalletHistoryBINANCETestCase(WalletHistoryTestCase, ModelTestCase):
    exchange = "BINANCE"
