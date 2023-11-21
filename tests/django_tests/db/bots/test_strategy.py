from datetime import datetime

from django.test import TestCase
from pytz import UTC

from django_napse.core.models import Bot, Strategy
from django_napse.simulations.models import SimulationQueue

"""
python tests/test_app/manage.py test tests.django_tests.bots.test_bot -v2 --keepdb --parallel
"""


class StrategyDefaultTestCase:
    def simple_create(self):
        return self.model.objects.create(config=self.config, architecture=self.architecture)

    @property
    def config(self):
        return self.model.config_class().objects.create(space=self.space, settings=self.config_settings)

    @property
    def architecture(self):
        return self.model.architecture_class().objects.create(constants=self.architecture_constants)

    def test_simulation(self):
        bot = Bot.objects.create(name="Test Bot", strategy=self.simple_create())
        simulation_queue = SimulationQueue.objects.create(
            space=self.space,
            bot=bot,
            start_date=datetime(2022, 1, 1, tzinfo=UTC),
            end_date=datetime(2022, 1, 5, tzinfo=UTC),
            investments={"USDT": 10000},
        )

        simulation_queue.run_quick_simulation(verbose=False)


class BotTypeCkeck(TestCase):
    def test_bot_type(self):
        subclasses = []
        for subclass_level in StrategyDefaultTestCase.__subclasses__():
            subclasses += subclass_level.__subclasses__()
        tested_strategies = {*[subclass.model for subclass in subclasses]}
        strategies = {*Strategy.__subclasses__()}
        if tested_strategies != strategies:
            error_msg = "You have untested Strategies. Check out the documentation to see how to test them (spoiler, it's really easy!)."
            error_msg += str(tested_strategies) + str(strategies)
            raise ValueError(error_msg)
