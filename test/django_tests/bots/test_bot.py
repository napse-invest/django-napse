from django.test import TestCase

from django_napse.core.models import Bot, Controller, EmptyBotConfig, EmptyStrategy, NapseSpace, Strategy
from django_napse.utils.errors import BotConfigError
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.bots.test_bot -v2 --keepdb --parallel
"""


class BotDefaultTestCase:
    def simple_create(self):
        return self.model.objects.create(name="Test Bot", strategy=self.strategy)

    @property
    def config(self):
        return self.strategy_class.config_class().objects.create(space=self.space, settings=self.config_settings)

    @property
    def architechture(self):
        return self.strategy_class.architechture_class().objects.create(**self.architechture_settings)

    @property
    def strategy(self):
        return self.strategy_class.objects.create(config=self.config, architechture=self.architechture)


class BotTypeCkeck(TestCase):
    def test_bot_type(self):
        subclasses = []
        for subclass_level in BotDefaultTestCase.__subclasses__():
            subclasses += subclass_level.__subclasses__()
        tested_strategies = {*[subclass.strategy_class for subclass in subclasses]}
        strategies = {*Strategy.__subclasses__()}
        if tested_strategies != strategies:
            error_msg = "You have untested Strategies. Check out the documentation to see how to test them (spoiler, it's really easy!)."
            raise ValueError(error_msg)


### Empty Bot ###
class EmptyBotTestCase(BotDefaultTestCase):
    model = Bot
    strategy_class = EmptyStrategy
    config_settings = {"empty": True}

    @property
    def architechture_settings(self):
        return {
            "controller": Controller.get(
                space=self.space,
                base="BTC",
                quote="USDT",
                interval="1m",
            ),
        }


class EmptyBotBINANCETestCase(EmptyBotTestCase, ModelTestCase):
    exchange = "BINANCE"
    exchange = "BINANCE"
