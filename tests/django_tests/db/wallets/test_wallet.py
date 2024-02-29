from django.db.utils import IntegrityError
from django.test import TestCase

from django_napse.core.models import Currency, CurrencyPydantic, SpaceWallet, Wallet, WalletPydantic
from django_napse.utils.errors import WalletError
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.wallets.test_wallet -v2 --keepdb --parallel
"""


class WalletTestCase(TestCase):
    def test_cant_create_wallet(self):
        with self.assertRaises(WalletError.CreateError):
            Wallet.objects.create(title="Test Wallet", owner=None)


class BaseWalletTestCase:
    def simple_create(self):
        return self.owner.wallet

    def test_error_duplicate_wallet(self):
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
    def test_exchange_account(self):
        wallet = self.simple_create()
        self.assertEqual(wallet.exchange_account, self.owner.exchange_account)

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
        wallet = self.simple_create()
        self.assertEqual(wallet.value_mbp(), 0)
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        Currency.objects.create(wallet=wallet, ticker="ETH", amount=0, mbp=1000)
        self.assertEqual(wallet.value_mbp(), 20000)

    def test_to_dict(self):
        wallet = self.simple_create()
        Currency.objects.create(wallet=wallet, ticker="BTC", amount=1, mbp=20000)
        Currency.objects.create(wallet=wallet, ticker="USDT", amount=1, mbp=1)
        self.assertEqual(
            wallet.to_dict(),
            WalletPydantic(
                title="Wallet for space Test Space",
                testing=True,
                locked=False,
                created_at=wallet.created_at,
                currencies={
                    "BTC": CurrencyPydantic(ticker="BTC", amount=1.0, mbp=20000.0),
                    "USDT": CurrencyPydantic(ticker="USDT", amount=1.0, mbp=1.0),
                },
            ),
        )


class SpaceWalletTestCase(BaseWalletTestCase):
    model = SpaceWallet

    def setUp(self):
        super().setUp()
        self.owner = self.space

    def test_with_real_exchange(self):
        self.space.wallet.top_up(ticker="BTC", amount=0.5, force=True)

    def test_space(self):
        wallet = self.simple_create()
        self.assertEqual(wallet.space, self.owner)

    def test_value_market_BTC(self):  # noqa: N802
        Currency.objects.create(wallet=self.space.wallet, ticker="BTC", amount=1, mbp=20000)
        self.assertTrue(self.space.wallet.value_market() > 0)

    def test_value_market_USDT(self):  # noqa: N802
        Currency.objects.create(wallet=self.space.wallet, ticker="USDT", amount=1, mbp=1)
        self.assertEqual(self.space.wallet.value_market(), 1)

    def test_value_zero(self):
        Currency.objects.create(wallet=self.space.wallet, ticker="BTC", amount=0, mbp=1)
        Currency.objects.create(wallet=self.space.wallet, ticker="USDT", amount=0, mbp=1)
        self.assertEqual(self.space.wallet.value_market(), 0)


class SpaceWalletBINANCETestCase(SpaceWalletTestCase, ModelTestCase):
    exchange = "BINANCE"


# class OrderWalletTestCase(BaseWalletTestCase):
#     model = OrderWallet

#     def setUp(self) -> None:
#         super().setUp()
#         config = EmptyBotConfig.objects.create(space=self.space, settings={"empty": True})
#         fleet = Fleet.objects.create(name="test_fleet", configs=[config], exchange_account=self.exchange_account)
#         bot = fleet.bots.first()
#         self.owner = Order.objects.create(bot=bot, buy_amount=100, sell_amount=100, price=1)
# def test_space(self):
#     wallet = self.simple_create()
#     self.assertEqual(wallet.space, self.owner.space)


# class OrderWalletBINANCETestCase(OrderWalletTestCase, ModelTestCase):
#     exchange = "BINANCE"


# class ConnectionWalletTestCase(BaseWalletTestCase, TestCase):
#     wallet_class = ConnectionWallet

#     def setUp(self) -> None:
#         self.owner = Conne.objects.create(name="Test Space", testing=True)
#         self.owner = Conne.objects.create(name="Test Space", testing=True)
#         self.owner = Conne.objects.create(name="Test Space", testing=True)
