from datetime import datetime

from pytz import UTC

from django_napse.core.models import Bot, Controller, EmptyBotConfig, EmptyStrategy, LBOPlugin, MBPPlugin, SBVPlugin, SinglePairArchitecture
from django_napse.simulations.models import SimulationQueue
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.db.simulations.test_simulation_queue -v2 --keepdb --parallel
"""


class SimulationQueueTestCase:
    model = SimulationQueue

    def simple_create(self):
        config = EmptyBotConfig.objects.create(space=self.space, settings={"empty": True})
        architecture = SinglePairArchitecture.objects.create(
            constants={
                "controller": Controller.get(
                    exchange_account=self.exchange_account,
                    base="BTC",
                    quote="USDT",
                    interval="1d",
                ),
            },
        )
        strategy = EmptyStrategy.objects.create(config=config, architecture=architecture)
        MBPPlugin.objects.create(strategy=strategy)
        LBOPlugin.objects.create(strategy=strategy)
        SBVPlugin.objects.create(strategy=strategy)
        bot = Bot.objects.create(name="Test Bot", strategy=strategy)
        return SimulationQueue.objects.create(
            space=self.space,
            bot=bot,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2020, 1, 5, tzinfo=UTC),
            investments={"USDT": 1000},
        )

    def test_quick_simulation(self):
        simulation_queue = self.simple_create()
        simulation_queue.run_quick_simulation(verbose=False)

    def test_irl_simulation(self):
        simulation_queue = self.simple_create()
        simulation_queue.run_irl_simulation(verbose=False)


class SimulationQueueBINANCETestCase(SimulationQueueTestCase, ModelTestCase):
    exchange = "BINANCE"
