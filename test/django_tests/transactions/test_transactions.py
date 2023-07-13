from django_napse.core.models import Currency, Exchange, ExchangeAccount, NapseSpace, SpaceWallet, Transaction
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.transactions.test_transactions -v2 --keepdb --parallel
"""


# class TransactionTestCase(ModelTestCase):
#     model = Transaction

#     def setUp(self):
#         self.exchange = Exchange.objects.create(
#             name="random exchange",
#             description="random description",
#         )
#         self.exchange_account = ExchangeAccount.objects.create(
#             exchange=self.exchange,
#             testing=True,
#             name="random exchange account 1",
#             description="random description",
#         )
#         self.space1 = NapseSpace.objects.create(
#             name="Test Space 1",
#             exchange_account=self.exchange_account,
#             description="This is a test space",
#         )
#         self.space2 = NapseSpace.objects.create(
#             name="Test Space 2",
#             exchange_account=self.exchange_account,
#             description="This is a test space",
#         )
#         self.from_wallet = SpaceWallet.objects.create(owner=self.space1, title="Test Wallet")
#         Currency.objects.create(wallet=self.from_wallet, ticker="BTC", amount=1, mbp=20000)
#         self.to_wallet = SpaceWallet.objects.create(owner=self.space2, title="Test Wallet")

#     def simple_create(self):
#         return Transaction.objects.create(from_wallet=self.from_wallet, to_wallet=self.to_wallet, amount=1, ticker="BTC")
