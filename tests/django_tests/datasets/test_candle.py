from datetime import datetime

from pytz import UTC

from django_napse.core.models import Controller
from django_napse.simulations.models import Candle, DataSet
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.datasets.test_candle -v2 --keepdb --parallel
"""


class CandleTestCase:
    model = Candle

    def simple_create(self):
        controller = Controller.get(
            exchange_account=self.exchange_account,
            base="BTC",
            quote="USDT",
            interval="1d",
        )
        dataset = DataSet.objects.create(
            controller=controller,
            start_date=datetime(2021, 1, 1, tzinfo=UTC),
            end_date=datetime(2021, 4, 1, tzinfo=UTC),
        )
        return Candle.objects.create(
            dataset=dataset,
            open_time=datetime(2020, 1, 1, tzinfo=UTC),
            open=1,
            high=2,
            low=0.5,
            close=1.5,
            volume=100,
        )


class CandleBINANCETestCase(CandleTestCase, ModelTestCase):
    exchange = "BINANCE"
