from datetime import datetime

from pytz import UTC

from django_napse.core.models import Bot, Controller, EmptyBotConfig, EmptyStrategy, SinglePairArchitecture
from django_napse.simulations.models import SimulationQueue
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.simulations.test_simulation_queue -v2 --keepdb --parallel
"""


class SimulationQueueTestCase:
    model = SimulationQueue

    def simple_create(self):
        config = EmptyBotConfig.objects.create(space=self.space, settings={"empty": True})
        architecture = SinglePairArchitecture.objects.create(
            controller=Controller.get(
                exchange_account=self.exchange_account,
                base="BTC",
                quote="USDT",
                interval="1m",
            ),
        )
        strategy = EmptyStrategy.objects.create(config=config, architecture=architecture)
        bot = Bot.objects.create(name="Test Bot", strategy=strategy)
        return SimulationQueue.objects.create(
            space=self.space,
            bot=bot,
            start_date=datetime(2021, 1, 1, tzinfo=UTC),
            end_date=datetime(2021, 1, 3, tzinfo=UTC),
            investments={"USDT": 1000},
        )

    def test_quick_simulation(self):
        simulation_queue = self.simple_create()
        print(simulation_queue)
        simulation_queue.run_quicksim()


class SimulationQueueBINANCETestCase(SimulationQueueTestCase, ModelTestCase):
    exchange = "BINANCE"
