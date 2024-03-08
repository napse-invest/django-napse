from django_napse.core.models import Credit, ExchangeAccount, Space, Transaction
from django_napse.utils.constants import TRANSACTION_TYPES
from django_napse.utils.errors import TransactionError
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.transactions.test_transactions -v2 --keepdb --parallel
"""


class TransactionTestCase:
    model = Transaction

    def setUp(self):
        self.from_wallet = self.space.wallet
        space = Space.objects.create(
            name="Test Space 2",
            exchange_account=self.exchange_account,
            description="This is a test space",
        )
        Credit.objects.create(wallet=self.from_wallet, amount=10, ticker="BTC")
        Credit.objects.create(wallet=space.wallet, amount=10, ticker="BTC")
        self.to_wallet = space.wallet

    def simple_create(self):
        return Transaction.objects.create(
            from_wallet=self.from_wallet,
            to_wallet=self.to_wallet,
            amount=1,
            ticker="BTC",
            transaction_type=TRANSACTION_TYPES.TRANSFER,
        )

    def test_error_same_space(self):
        exchange_account2 = ExchangeAccount.objects.create(
            exchange=self.exchange_account.exchange,
            testing=True,
            name="random exchange account 2",
            description="random description",
        )
        space2 = Space.objects.create(
            name="Test Space 2",
            exchange_account=exchange_account2,
            description="This is a test space",
        )
        wallet = space2.wallet
        with self.assertRaises(TransactionError.DifferentAccountError):
            Transaction.objects.create(
                from_wallet=self.from_wallet,
                to_wallet=wallet,
                amount=1,
                ticker="BTC",
                transaction_type=TRANSACTION_TYPES.TRANSFER,
            )

    def test_amount_zero(self):
        transaction = Transaction.objects.create(
            from_wallet=self.from_wallet,
            to_wallet=self.to_wallet,
            amount=0,
            ticker="BTC",
            transaction_type=TRANSACTION_TYPES.TRANSFER,
        )
        self.assertIsNone(transaction)

    def test_error_transaction_type(self):
        with self.assertRaises(TransactionError.InvalidTransactionError):
            Transaction.objects.create(
                from_wallet=self.from_wallet,
                to_wallet=self.to_wallet,
                amount=1,
                ticker="BTC",
                transaction_type="random transaction type",
            )


class TransactionBINANCETestCase(TransactionTestCase, ModelTestCase):
    exchange = "BINANCE"
