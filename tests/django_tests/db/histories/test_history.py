from django_napse.core.models import History, HistoryDataPoint, HistoryDataPointField
from django_napse.utils.constants import HISTORY_DATAPOINT_FIELDS
from django_napse.utils.errors import HistoryError
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.db.histories -v2 --keepdb --parallel
"""


class HistoryTestCase:
    model = History

    def simple_create(self):
        return self.model.objects.create()

    def test_data_points(self):
        info = [
            [
                {"key": HISTORY_DATAPOINT_FIELDS.AMOUNT, "value": "1", "target_type": "float"},
                {"key": HISTORY_DATAPOINT_FIELDS.ASSET, "value": "BTC", "target_type": "str"},
                {"key": HISTORY_DATAPOINT_FIELDS.PRICE, "value": "123", "target_type": "float"},
                {"key": HISTORY_DATAPOINT_FIELDS.MBP, "value": "100", "target_type": "float"},
                {"key": HISTORY_DATAPOINT_FIELDS.LBO, "value": "7", "target_type": "float"},
            ]
            for _ in range(100)
        ]
        history = self.simple_create()
        for data_point_info in info:
            data_point = HistoryDataPoint.objects.create(history=history)
            for field_info in data_point_info:
                HistoryDataPointField.objects.create(history_data_point=data_point, **field_info)
        self.assertEqual(history.data_points.count(), len(info))

    def test_invalid_data_point(self):
        history = self.simple_create()
        data_point = HistoryDataPoint.objects.create(history=history)

        with self.assertRaises(HistoryError.InvalidDataPointFieldKey):
            HistoryDataPointField.objects.create(history_data_point=data_point, key="INVALID", value="1", target_type="float")


class HistoryBINANCETestCase(HistoryTestCase, ModelTestCase):
    exchange = "BINANCE"
