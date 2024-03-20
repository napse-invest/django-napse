from typing import ClassVar

from django_napse.core.models import Controller, EmptyStrategy
from django_napse.utils.model_test_case import ModelTestCase
from tests.django_tests.db.bots.test_strategy import StrategyDefaultTestCase

"""
python tests/test_app/manage.py test tests.django_tests.bots.test_strategies.test_empty_bot -v2 --keepdb --parallel
"""


class EmptyBotTestCase(StrategyDefaultTestCase):
    model = EmptyStrategy
    config_settings: ClassVar = {"empty": True}

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


class EmptyBotBINANCETestCase(EmptyBotTestCase, ModelTestCase):
    exchange = "BINANCE"
