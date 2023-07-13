from unittest import skipIf

from django.db.utils import IntegrityError
from django.test import TestCase

from django_napse.core.models import (
    BinanceAccount,
    BotConfig,
    Currency,
    Exchange,
    ExchangeAccount,
    Fleet,
    NapseSpace,
    Order,
    OrderWallet,
    SpaceWallet,
    Wallet,
)
from django_napse.core.settings import napse_settings
from django_napse.utils.errors import WalletError
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.wallets.test_wallet -v2 --keepdb --parallel
"""


class WalletTestCase(TestCase):
    def test_cant_create_wallet(self):
        with self.assertRaises(WalletError.CreateError):
            Wallet.objects.create(title="Test Wallet", owner=None)


class BaseWalletTestCase:
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

    def simple_create(self):
        wallet = self.model.objects.create(title="Test Wallet", owner=self.owner)
        Currency.objects.create(wallet=wallet, ticker="MATIC", amount=1, mbp=20000)
        return wallet

    def test_error_duplicate_wallet(self):
        self.model.objects.create(title="Test Wallet", owner=self.owner)
        with self.assertRaises(IntegrityError):
            self.model.objects.create(title="Test Wallet", owner=self.owner)

    def test_property_testing(self):
        wallet = self.simple_create()
        self.assertTrue(wallet.testing)

    # Spend
    def test_spend_security(self):
        wallet = self.simple_create()
        with self.assertRaises(WalletError.SpendError):
            wallet.spend(ticker="BTC", amount=0.5)

    def test_force_spend(self):
        wallet = self.simple_create()
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        wallet.spend(ticker="BTC", amount=0.5, force=True)

    def test_insufficient_funds(self):
        wallet = self.simple_create()
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        with self.assertRaises(WalletError.SpendError):
            wallet.spend(ticker="BTC", amount=2, force=True)

    def test_non_existing_funds(self):
        wallet = self.simple_create()
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        with self.assertRaises(WalletError.SpendError):
            wallet.spend(ticker="ETH", amount=2, force=True)

    def test_spend_negative(self):
        wallet = self.simple_create()
        with self.assertRaises(ValueError):
            wallet.spend(ticker="BTC", amount=-2, force=True)

    def test_error_spend_locked(self):
        wallet = self.simple_create()
        wallet.locked = True
        wallet.save()
        with self.assertRaises(TimeoutError):
            wallet.spend(ticker="BTC", amount=2, force=True)

    # Top Up
    def test_topup_security(self):
        wallet = self.simple_create()
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        with self.assertRaises(WalletError.TopUpError):
            wallet.top_up(ticker="BTC", amount=0.5)

    def test_force_topup(self):
        wallet = self.simple_create()
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        wallet.top_up(ticker="BTC", amount=0.5, mbp=1, force=True)

    def test_error_topup_locked(self):
        wallet = self.simple_create()
        wallet.locked = True
        wallet.save()
        with self.assertRaises(TimeoutError):
            wallet.top_up(ticker="BTC", amount=2, mbp=1, force=True)

    def test_topup_negative(self):
        wallet = self.simple_create()
        with self.assertRaises(ValueError):
            wallet.top_up(ticker="BTC", amount=-2, mbp=1, force=True)

    # Other
    def test_space(self):  # pragma: no cover
        error_msg = "Please implement this test in the child class."
        raise NotImplementedError(error_msg)

    def test_has_funds(self):
        wallet = self.simple_create()
        self.assertFalse(wallet.has_funds(ticker="BTC", amount=1))
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        self.assertTrue(wallet.has_funds(ticker="BTC", amount=1))

    def test_get_amout(self):
        wallet = self.simple_create()
        self.assertEqual(wallet.get_amount(ticker="BTC"), 0)
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        self.assertEqual(wallet.get_amount(ticker="BTC"), 1)

    def test_value_mbp(self):
        wallet = self.model.objects.create(title="Test Wallet", owner=self.owner)
        self.assertEqual(wallet.value_mbp(), 0)
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        Currency.objects.create(wallet=wallet, ticker="ETH", amount=0, mbp=1000)
        self.assertEqual(wallet.value_mbp(), 20000)

    def test_to_dict(self):
        wallet = self.model.objects.create(title="Test Wallet", owner=self.owner)
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        Currency.objects.create(wallet=wallet, ticker="USDT", amount=1, mbp=1)
        self.assertEqual(
            wallet.to_dict(),
            {
                "title": "Test Wallet",
                "testing": True,
                "locked": False,
                "created_at": wallet.created_at,
                "currencies": {"BTC": {"amount": 1.0, "mbp": 20000.0}, "USDT": {"amount": 1.0, "mbp": 1.0}},
            },
        )


class SpaceWalletTestCase(BaseWalletTestCase, ModelTestCase):
    model = SpaceWallet

    def setUp(self):
        super().setUp()
        self.owner = NapseSpace.objects.create(
            name="Test Space",
            exchange_account=self.exchange_account,
            description="This is a test space",
        )

    def test_with_real_exchange(self):
        for account in BinanceAccount.objects.all():
            space = account.spaces.first()
            wallet = self.model.objects.create(title="Test Wallet", owner=space)
            wallet.top_up(ticker="BTC", amount=0.5, force=True)

    def test_space(self):
        wallet = self.simple_create()
        self.assertEqual(wallet.space, self.owner)

    @skipIf(napse_settings.IS_IN_PIPELINE, "IP will be refused")
    def test_value_market_BTC(self):
        for account in BinanceAccount.objects.all():
            space = account.spaces.first()
            wallet = self.model.objects.create(title="Test Wallet", owner=space)
            Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
            self.assertTrue(wallet.value_market() > 0)

    @skipIf(napse_settings.IS_IN_PIPELINE, "IP will be refused")
    def test_value_market_USDT(self):
        for account in BinanceAccount.objects.all():
            space = account.spaces.first()
            wallet = self.model.objects.create(title="Test Wallet", owner=space)
            Currency.objects.create(wallet=wallet, ticker="USDT", amount=1, mbp=1)
            self.assertEqual(wallet.value_market(), 1)

    @skipIf(napse_settings.IS_IN_PIPELINE, "IP will be refused")
    def test_value_zero(self):
        for account in BinanceAccount.objects.all():
            space = account.spaces.first()
            wallet = self.model.objects.create(title="Test Wallet", owner=space)
            Currency.objects.create(wallet=wallet, ticker="BTC", amount=0, mbp=1)
            Currency.objects.create(wallet=wallet, ticker="USDT", amount=0, mbp=1)
            self.assertEqual(wallet.value_market(), 0)


class OrderWalletTestCase(BaseWalletTestCase, TestCase):
    model = OrderWallet

    def setUp(self) -> None:
        super().setUp()
        space = NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")
        config = BotConfig.objects.create(bot_type="Bot", name="test_bot", pair="MATICUSDT", interval="1m", space=space)
        fleet = Fleet.objects.create(name="test_fleet", configs=[config], exchange_account=self.exchange_account)
        bot = fleet.bots.first()
        self.owner = Order.objects.create(bot=bot, buy_amount=100, sell_amount=100, price=1)
        self.owner.wallet.delete()

    def test_space(self):
        wallet = self.simple_create()
        self.assertEqual(wallet.space, self.owner.space)


# class ConnectionWalletTestCase(BaseWalletTestCase, TestCase):
#     wallet_class = ConnectionWallet

#     def setUp(self) -> None:
#         self.owner = Conne.objects.create(name="Test Space", testing=True)
