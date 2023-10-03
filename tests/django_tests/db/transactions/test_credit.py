from django_napse.core.models import Credit
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.transactions.test_credit -v2 --keepdb --parallel
"""


class CreditTestCase:
    model = Credit

    def simple_create(self):
        return Credit.objects.create(
            wallet=self.space.wallet,
            amount=1,
            ticker="BTC",
        )

    def test_empty_credit(self):
        credit = Credit.objects.create(
            wallet=self.space.wallet,
            amount=0,
            ticker="BTC",
        )
        self.assertIsNone(credit)

    def test_correct_amount(self):
        self.simple_create()
        self.assertEqual(self.space.wallet.get_amount("BTC"), 1)
        self.simple_create()
        self.assertEqual(self.space.wallet.get_amount("BTC"), 2)


class CreditBINANCETestCase(CreditTestCase, ModelTestCase):
    exchange = "BINANCE"
