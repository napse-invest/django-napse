from datetime import datetime
from typing import ClassVar

from pytz import UTC

from django_napse.core.models import Bot, Controller, EmptyBotConfig, EmptyStrategy, SinglePairArchitecture
from django_napse.simulations.models import SimulationQueue

"""
python tests/test_app/manage.py test tests.django_tests.bots.test_plugin -v2 --keepdb --parallel
"""


class PluginDefaultTestCase:
    strategy_class = EmptyStrategy
    config_settings: ClassVar = {"empty": True}

    def simple_create(self):
        return self.model.objects.create(strategy=self.strategy)

    @property
    def config(self):
        return self.strategy_class.config_class().objects.create(space=self.space, settings=self.config_settings)

    @property
    def architecture(self):
        return self.strategy_class.architecture_class().objects.create(constants=self.architecture_constants)

    @property
    def strategy(self):
        return self.strategy_class.objects.create(config=self.config, architecture=self.architecture)

    @property
    def architecture_constants(self):
        return {
            "controller": Controller.get(
                exchange_account=self.exchange_account,
                base="BTC",
                quote="USDT",
                interval="1m",
            ),
        }

    def test_simulation(self):
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
        self.model.objects.create(strategy=strategy)
        bot = Bot.objects.create(name="Test Bot", strategy=strategy)
        simulation_queue = SimulationQueue.objects.create(
            space=self.space,
            bot=bot,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2020, 1, 5, tzinfo=UTC),
            investments={"USDT": 10000},
        )

        simulation_queue.run_quick_simulation(verbose=False)
