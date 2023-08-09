from test.django_tests.bots.test_bot import BotDefaultTestCase

from django_napse.core.models import Bot, Controller, EmptyStrategy
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.bots.test_empty_bot -v2 --keepdb --parallel
"""


class EmptyBotTestCase(BotDefaultTestCase):
    model = Bot
    strategy_class = EmptyStrategy
    config_settings = {"empty": True}

    @property
    def architecture_settings(self):
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
