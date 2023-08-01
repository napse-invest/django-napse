from django_napse.core.models import Currency, EmptyBotConfig, Exchange, ExchangeAccount, Fleet, NapseSpace, Order, Transaction
from django_napse.utils.constants import TRANSACTION_TYPES
from django_napse.utils.errors import TransactionError
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.transactions.test_transactions -v2 --keepdb --parallel
"""


class TransactionTestCase(ModelTestCase):
    model = Transaction

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
        self.space1 = NapseSpace.objects.create(
            name="Test Space 1",
            exchange_account=self.exchange_account,
            description="This is a test space",
        )

        self.from_wallet = self.space1.wallet
        Currency.objects.create(wallet=self.from_wallet, ticker="BTC", amount=1, mbp=20000)

        config = EmptyBotConfig.objects.create(space=self.space1)
        fleet = Fleet.objects.create(name="test_fleet", configs=[config], exchange_account=self.exchange_account)
        bot = fleet.bots.first()
        order = Order.objects.create(bot=bot, buy_amount=100, sell_amount=100, price=1)
        self.to_wallet = order.wallet

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
            exchange=self.exchange,
            testing=True,
            name="random exchange account 2",
            description="random description",
        )
        space2 = NapseSpace.objects.create(
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
