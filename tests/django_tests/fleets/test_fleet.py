from django_napse.core.models import Bot, Controller, Credit, EmptyBotConfig, EmptyStrategy, Fleet, SinglePairArchitecture
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.fleets.test_fleet -v2 --keepdb --parallel
"""


class FleetTestCase:
    model = Fleet

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
        return self.model.objects.create(
            name="Test Fleet",
            exchange_account=self.exchange_account,
            clusters=[
                {
                    "bot": bot,
                    "share": 0.7,
                    "breakpoint": 1000,
                    "autoscale": False,
                },
                {
                    "bot": bot,
                    "share": 0.3,
                    "breakpoint": 1000,
                    "autoscale": True,
                },
            ],
        )

    def test_invest(self):
        Credit.objects.create(wallet=self.space.wallet, amount=1000, ticker="USDT")
        fleet = self.simple_create()
        connections = fleet.invest(self.space, 1000, "USDT")
        self.assertEqual(self.space.wallet.get_amount("USDT"), 0)
        self.assertEqual(connections[0].wallet.get_amount("USDT"), 700)
        self.assertEqual(connections[1].wallet.get_amount("USDT"), 300)

    def test_invest_twice(self):
        Credit.objects.create(wallet=self.space.wallet, amount=2000, ticker="USDT")
        fleet = self.simple_create()
        fleet.invest(self.space, 1000, "USDT")
        connections = fleet.invest(self.space, 1000, "USDT")
        self.assertEqual(self.space.wallet.get_amount("USDT"), 0)
        self.assertEqual(connections[0].wallet.get_amount("USDT"), 1400)
        self.assertEqual(connections[1].wallet.get_amount("USDT"), 600)


class FleetBINANCETestCase(FleetTestCase, ModelTestCase):
    exchange = "BINANCE"
