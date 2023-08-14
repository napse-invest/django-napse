from datetime import timedelta
from test.django_tests.bots.test_strategy import StrategyDefaultTestCase

from django_napse.core.models import Controller, TurboDCAStrategy
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.bots.test_strategies.test_turbo_dca -v2 --keepdb --parallel
"""


class TurboDCATestCase(StrategyDefaultTestCase):
    model = TurboDCAStrategy
    config_settings = {"timeframe": timedelta(days=1), "percentage": 1}

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


class TurboDCABINANCETestCase(TurboDCATestCase, ModelTestCase):
    exchange = "BINANCE"
