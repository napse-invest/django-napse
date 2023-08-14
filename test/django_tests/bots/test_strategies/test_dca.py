from datetime import timedelta
from test.django_tests.bots.test_strategy import StrategyDefaultTestCase

from django_napse.core.models import Controller, DCAStrategy
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.bots.test_strategies.test_dca -v2 --keepdb --parallel
"""


class DCATestCase(StrategyDefaultTestCase):
    model = DCAStrategy
    config_settings = {"timeframe": timedelta(days=1)}

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


class DCABINANCETestCase(DCATestCase, ModelTestCase):
    exchange = "BINANCE"
