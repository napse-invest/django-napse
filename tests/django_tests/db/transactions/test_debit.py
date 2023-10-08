from django_napse.core.models import Credit, Debit
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.transactions.test_debit -v2 --keepdb --parallel
"""


class DebitTestCase:
    model = Debit

    def simple_create(self):
        Credit.objects.create(wallet=self.space.wallet, amount=10, ticker="BTC")
        return Debit.objects.create(
            wallet=self.space.wallet,
            amount=1,
            ticker="BTC",
        )

    def test_empty_credit(self):
        debit = Debit.objects.create(
            wallet=self.space.wallet,
            amount=0,
            ticker="BTC",
        )
        self.assertIsNone(debit)

    def test_correct_amount(self):
        Credit.objects.create(wallet=self.space.wallet, amount=10, ticker="BTC")
        Debit.objects.create(
            wallet=self.space.wallet,
            amount=1,
            ticker="BTC",
        )
        self.assertEqual(self.space.wallet.get_amount("BTC"), 9)
        Debit.objects.create(
            wallet=self.space.wallet,
            amount=1,
            ticker="BTC",
        )
        self.assertEqual(self.space.wallet.get_amount("BTC"), 8)


class DebitBINANCETestCase(DebitTestCase, ModelTestCase):
    exchange = "BINANCE"
