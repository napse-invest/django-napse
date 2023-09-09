from django_napse.core.models import Bot, Connection, Controller, EmptyBotConfig, EmptyStrategy, Order, OrderBatch, SinglePairArchitecture
from django_napse.utils.constants import SIDES
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.orders.test_order -v2 --keepdb --parallel
"""


class OrderTestCase:
    model = Order

    def simple_create(self):
        config = EmptyBotConfig.objects.create(space=self.space, settings={"empty": True})
        controller = Controller.get(
            exchange_account=self.exchange_account,
            base="BTC",
            quote="USDT",
            interval="1m",
        )
        architecture = SinglePairArchitecture.objects.create(constants={"controller": controller})
        strategy = EmptyStrategy.objects.create(config=config, architecture=architecture)
        bot = Bot.objects.create(name="Test Bot", strategy=strategy)
        connection = Connection.objects.create(owner=self.space.wallet, bot=bot)
        connection.wallet.top_up(amount=10000, ticker="USDT", force=True)
        batch = OrderBatch.objects.create(controller=controller)
        return Order.objects.create(
            batch=batch,
            connection=connection,
            asked_for_amount=10,
            asked_for_ticker="USDT",
            price=30000,
            pair="BTCUSDT",
            side=SIDES.BUY,
        )


class OrderBINANCETestCase(OrderTestCase, ModelTestCase):
    exchange = "BINANCE"
