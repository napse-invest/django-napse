from django_napse.core.models import BotConfig, Exchange, ExchangeAccount, Fleet, NapseSpace, Order
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.orders.test_orders -v2 --keepdb --parallel
"""


class OrderTestCase(ModelTestCase):
    model = Order

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
        self.space = NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")

    def simple_create(self):
        config = BotConfig.objects.create(bot_type="Bot", name="test_bot", pair="MATICUSDT", interval="1m", space=self.space)
        fleet = Fleet.objects.create(name="test_fleet", configs=[config], exchange_account=self.exchange_account)
        bot = fleet.bots.first()
        return Order.objects.create(bot=bot, buy_amount=100, sell_amount=100, price=1)
