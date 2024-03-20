from django_napse.core.models import Bot, Controller, Credit, EmptyBotConfig, EmptyStrategy, Fleet, SinglePairArchitecture, Space
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.db.fleets.test_fleet -v2 --keepdb --parallel
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
                    "template_bot": bot,
                    "share": 0.7,
                    "breakpoint": 1000,
                    "autoscale": False,
                },
                {
                    "template_bot": bot,
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

    def _two_spaces_on_same_fleet(self):
        fleet = self.simple_create()

        space = Space.objects.create(name="Random Space", exchange_account=self.exchange_account, description="This is a test space")
        Credit.objects.create(wallet=space.wallet, amount=2000, ticker="USDT")
        fleet.invest(space, 1000, "USDT")

        Credit.objects.create(wallet=self.space.wallet, amount=2000, ticker="USDT")
        fleet.invest(self.space, 1000, "USDT")

        return fleet

    def test_value(self):
        Credit.objects.create(wallet=self.space.wallet, amount=1000, ticker="USDT")
        fleet = self.simple_create()
        fleet.invest(self.space, 1000, "USDT")
        self.assertEqual(fleet.value, 1000)

    def test_value_with_two_spaces(self):
        fleet = self._two_spaces_on_same_fleet()
        self.assertEqual(fleet.value, 2000)

    def test_space_frame_value(self):
        Credit.objects.create(wallet=self.space.wallet, amount=1000, ticker="USDT")
        fleet = self.simple_create()
        fleet.invest(self.space, 1000, "USDT")
        self.assertEqual(fleet.space_frame_value(self.space), 1000)

    def test_space_frame_value_with_two_spaces(self):
        fleet = self._two_spaces_on_same_fleet()
        self.assertEqual(fleet.space_frame_value(self.space), 1000)


class FleetBINANCETestCase(FleetTestCase, ModelTestCase):
    exchange = "BINANCE"
