from typing import ClassVar

from django_napse.core.models import Bot, Controller, EmptyStrategy
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.bots.test_bot -v2 --keepdb --parallel
"""


class BotDefaultTestCase:
    model = Bot
    strategy_class = EmptyStrategy
    config_settings: ClassVar = {"empty": True}

    @property
    def architecture_constants(self):
        return {
            "controller": Controller.get(
                exchange_account=self.exchange_account,
                base="BTC",
                quote="USDT",
                interval="1d",
            ),
        }

    def simple_create(self):
        return self.model.objects.create(name="Test Bot", strategy=self.strategy)

    @property
    def config(self):
        return self.strategy_class.config_class().objects.create(space=self.space, settings=self.config_settings)

    @property
    def architecture(self):
        return self.strategy_class.architecture_class().objects.create(constants=self.architecture_constants)

    @property
    def strategy(self):
        return self.strategy_class.objects.create(config=self.config, architecture=self.architecture)


class BotBINANCETestCase(BotDefaultTestCase, ModelTestCase):
    exchange = "BINANCE"
