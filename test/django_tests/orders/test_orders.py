from django_napse.core.models import Bot, Connection, Controller, EmptyBotConfig, EmptyStrategy, Order, SinglePairArchitecture
from django_napse.utils.constants import SIDES
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.orders.test_orders -v2 --keepdb --parallel
"""


class OrderTestCase:
    model = Order

    def simple_create(self):
        config = EmptyBotConfig.objects.create(space=self.space, settings={"empty": True})
        architecture = SinglePairArchitecture.objects.create(
            controller=Controller.get(
                space=self.space,
                base="BTC",
                quote="USDT",
                interval="1m",
            ),
        )
        strategy = EmptyStrategy.objects.create(config=config, architecture=architecture)
        bot = Bot.objects.create(name="Test Bot", strategy=strategy)
        connection = Connection.objects.create(space=self.space, bot=bot)
        connection.wallet.top_up(amount=10000, ticker="USDT", force=True)
        return Order.objects.create(connection=connection, amount=0.1, price=30000, pair="BTCUSDT", side=SIDES.BUY)


class OrderBINANCETestCase(OrderTestCase, ModelTestCase):
    exchange = "BINANCE"
