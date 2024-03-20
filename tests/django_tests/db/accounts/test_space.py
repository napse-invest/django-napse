from django.db.utils import IntegrityError

from django_napse.core.models import Bot, Controller, Credit, EmptyBotConfig, EmptyStrategy, Fleet, SinglePairArchitecture, Space
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.db.accounts.test_space -v2 --keepdb --parallel
"""


class SpaceTestCase:
    model = Space

    def simple_create(self):
        return Space.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")

    def test_error_create_napse_space_with_same_name(self):
        Space.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")
        with self.assertRaises(IntegrityError):
            Space.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")

    def _build_fleet_context(self):
        config = EmptyBotConfig.objects.create(space=self.space, settings={"empty": True})
        controller = Controller.get(
            exchange_account=self.exchange_account,
            base="BTC",
            quote="USDT",
            interval="1m",
        )
        architecture = SinglePairArchitecture.objects.create(constants={"controller": controller})
        strategy = EmptyStrategy.objects.create(config=config, architecture=architecture)
        template_bot = Bot.objects.create(name="Test Bot", strategy=strategy)
        fleet = Fleet.objects.create(
            name="Test Fleet",
            exchange_account=self.exchange_account,
            clusters=[
                {
                    "template_bot": template_bot,
                    "share": 0.7,
                    "breakpoint": 1000,
                    "autoscale": False,
                },
                {
                    "template_bot": template_bot,
                    "share": 0.3,
                    "breakpoint": 1000,
                    "autoscale": True,
                },
            ],
        )
        Credit.objects.create(wallet=self.space.wallet, amount=1000, ticker="USDT")
        connections = fleet.invest(self.space, 1000, "USDT")
        return fleet, connections

    def test_value_property(self):
        self._build_fleet_context()
        self.assertEqual(self.space.value, 1000)

    def test_fleets_property(self):
        fleet, _ = self._build_fleet_context()
        self.assertEqual(len(self.space.fleets), 1)
        self.assertEqual(self.space.fleets[0].uuid, fleet.uuid)


class NaspeSpaceBINANCETestCase(SpaceTestCase, ModelTestCase):
    exchange = "BINANCE"
