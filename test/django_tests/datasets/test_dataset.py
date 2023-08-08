from datetime import datetime

from pytz import UTC

from django_napse.core.models import Controller
from django_napse.simulations.models import DataSet
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.datasets.test_dataset -v2 --keepdb --parallel
"""


class DataSetTestCase:
    model = DataSet

    def simple_create(self):
        controller = Controller.get(
            space=self.space,
            base="BTC",
            quote="USDT",
            interval="1d",
        )
        return DataSet.objects.create(
            controller=controller,
            start_date=datetime(2021, 1, 1, tzinfo=UTC),
            end_date=datetime(2021, 4, 1, tzinfo=UTC),
        )

    def test_download_on_top(self):
        dataset = self.simple_create()
        new = DataSet.objects.create(
            controller=dataset.controller,
            start_date=datetime(2021, 1, 1, tzinfo=UTC),
            end_date=datetime(2021, 5, 1, tzinfo=UTC),
        )
        new.info()


class DataSetBINANCETestCase(DataSetTestCase, ModelTestCase):
    exchange = "BINANCE"
