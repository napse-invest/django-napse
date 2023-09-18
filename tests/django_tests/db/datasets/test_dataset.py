from datetime import datetime

from pytz import UTC

from django_napse.core.models import Controller
from django_napse.simulations.models import DataSet
from django_napse.utils.errors import DataSetError
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.datasets.test_dataset -v2 --keepdb --parallel
"""


class DataSetTestCase:
    model = DataSet

    def simple_create(self):
        controller = Controller.get(
            exchange_account=self.exchange_account,
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
        DataSet.objects.create(
            controller=dataset.controller,
            start_date=datetime(2021, 1, 1, tzinfo=UTC),
            end_date=datetime(2021, 5, 1, tzinfo=UTC),
        )

    def test_info_small(self):
        controller = Controller.get(
            exchange_account=self.exchange_account,
            base="BTC",
            quote="USDT",
            interval="1d",
        )
        dataset = DataSet.objects.create(
            controller=controller,
            start_date=datetime(2021, 1, 1, tzinfo=UTC),
            end_date=datetime(2021, 1, 3, tzinfo=UTC),
        )
        dataset.info(verbose=False)

    def test_error_save_completion_lt_0(self):
        dataset = self.simple_create()
        dataset.completion = -1
        with self.assertRaises(DataSetError.InvalidSettings):
            dataset.save()

    def test_error_save_completion_gt_100(self):
        dataset = self.simple_create()
        dataset.completion = 101
        with self.assertRaises(DataSetError.InvalidSettings):
            dataset.save()

    def test_error_save_status_not_in_download_status(self):
        dataset = self.simple_create()
        dataset.status = "random status"
        with self.assertRaises(DataSetError.InvalidSettings):
            dataset.save()

    def test_error_already_downloading(self):
        dataset = self.simple_create()
        dataset.status = "DOWNLOADING"
        dataset.save()
        with self.assertRaises(DataSetError.InvalidSettings):
            dataset.set_downloading()

    def test_error_already_idle(self):
        dataset = self.simple_create()
        dataset.status = "IDLE"
        dataset.save()
        with self.assertRaises(DataSetError.InvalidSettings):
            dataset.set_idle()

    def test_is_finished(self):
        dataset = self.simple_create()
        self.assertTrue(dataset.is_finished())

        dataset.status = "DOWNLOADING"
        dataset.completion = 50
        dataset.save()
        self.assertFalse(dataset.is_finished())

        dataset.status = "DOWNLOADING"
        dataset.completion = 100
        dataset.save()
        self.assertFalse(dataset.is_finished())

        dataset.status = "IDLE"
        dataset.completion = 50
        dataset.save()
        self.assertFalse(dataset.is_finished())


class DataSetBINANCETestCase(DataSetTestCase, ModelTestCase):
    exchange = "BINANCE"
