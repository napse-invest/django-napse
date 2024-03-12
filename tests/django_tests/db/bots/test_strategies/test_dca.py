from datetime import timedelta
from typing import ClassVar

from django_napse.core.models import Controller, DCAStrategy
from django_napse.utils.model_test_case import ModelTestCase
from tests.django_tests.db.bots.test_strategy import StrategyDefaultTestCase

"""
python tests/test_app/manage.py test tests.django_tests.bots.test_strategies.test_dca -v2 --keepdb --parallel
"""


class DCATestCase(StrategyDefaultTestCase):
    model = DCAStrategy
    config_settings: ClassVar = {"timeframe": timedelta(days=1)}

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


class DCABINANCETestCase(DCATestCase, ModelTestCase):
    exchange = "BINANCE"
