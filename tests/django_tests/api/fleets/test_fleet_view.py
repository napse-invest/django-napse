from django_napse.api.fleets import FleetView
from django_napse.core.models import Bot, Controller, EmptyBotConfig, EmptyStrategy, Fleet, SinglePairArchitecture
from django_napse.utils.api_test_case import APITestCase, ViewTest
from django_napse.utils.dict_comparison import compare_responses

"""
python tests/test_app/manage.py test tests.django_tests.api.fleets.test_fleet_view -v2 --keepdb --parallel
"""


class ListFleetViewTest(ViewTest):
    def __init__(self, *args, **kwargs):
        """Build a fleet."""
        super().__init__(*args, **kwargs)
        # create simple fleet
        config = EmptyBotConfig.objects.create(space=self.testcase_instance.space, settings={"empty": True})
        # config = EmptyBotConfig.objects.get(space=self.testcase_instance.space)
        print(f"config: {config}")
        controller = Controller.get(
            exchange_account=self.testcase_instance.exchange_account,
            base="BTC",
            quote="USDT",
            interval="1m",
        )
        architecture = SinglePairArchitecture.objects.create(constants={"controller": controller})
        strategy = EmptyStrategy.objects.create(config=config, architecture=architecture)
        bot = Bot.objects.create(name="Test Bot", strategy=strategy)
        self.fleet = Fleet.objects.create(
            name="Test Fleet",
            exchange_account=self.testcase_instance.exchange_account,
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

    def check_response(self, response) -> bool:
        return compare_responses(
            response.data[0],
            {
                "uuid": str(),
                "name": str(),
                "value": float(),
                "bot_count": int(),
            },
        )

    def run(self):
        print("list run")
        return [
            {
                "name": "response",
                "setup": self.setup(),
                "status_code": 200,
                "checks": [self.check_response],
            },
        ]


class RetrieveFleetViewTest(ViewTest):
    def __init__(self, *args, **kwargs):
        """Build a fleet."""
        super().__init__(*args, **kwargs)
        # create simple fleet
        config = EmptyBotConfig.objects.create(space=self.testcase_instance.space, settings={"empty": True})
        controller = Controller.get(
            exchange_account=self.testcase_instance.exchange_account,
            base="BTC",
            quote="USDT",
            interval="1m",
        )
        architecture = SinglePairArchitecture.objects.create(constants={"controller": controller})
        strategy = EmptyStrategy.objects.create(config=config, architecture=architecture)
        bot = Bot.objects.create(name="Test Bot", strategy=strategy)
        self.fleet = Fleet.objects.create(
            name="Test Fleet",
            exchange_account=self.testcase_instance.exchange_account,
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

    def check_response(self, response) -> bool:
        return compare_responses(
            response.data,
            {
                "uuid": str(),
                "name": str(),
                "created_at": str(),
                "statistics": {
                    "value": float(),
                    "order_count_30": float(),
                    "change_30": None,
                },
                "wallet": {},
                # "history": {},
                "bots": [],
            },
            authorize_abstract_comparison=True,
        )

    def run(self):
        print("retrieve run")
        return [
            {
                "name": "response",
                "setup": self.setup(),
                "status_code": 200,
                "checks": [self.check_response],
            },
        ]


class FleetViewTestCase:
    # def test_list(self):
    #     self.run_tests("list")

    # def test_retrieve(self):
    #     self.run_tests("list")

    def setup(self):
        list_test = ListFleetViewTest(self)
        # retrieve_test = RetrieveFleetViewTest(self)

        return {
            "list": {
                "url_name": "fleet-list",
                "view": FleetView,
                "method": "GET",
                "tests": list_test.run(),
            },
            # "retrieve": {
            #     "url_name": "fleet-detail",
            #     "view": FleetView,
            #     "method": "GET",
            #     "kwargs": {"pk": self.retrieve_test.fleet.uuid},
            #     "tests": retrieve_test.run(),
            # },
        }


class FleetViewAPIBinanceTestCase(FleetViewTestCase, APITestCase):
    exchange = "BINANCE"
