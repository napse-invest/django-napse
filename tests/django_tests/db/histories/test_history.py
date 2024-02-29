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
                {"key": HISTORY_DATAPOINT_FIELDS.AMOUNT, "value": 1},
                {"key": HISTORY_DATAPOINT_FIELDS.ASSET, "value": "BTC"},
                {"key": HISTORY_DATAPOINT_FIELDS.PRICE, "value": 123.0},
                {"key": HISTORY_DATAPOINT_FIELDS.MBP, "value": 100},
                {"key": HISTORY_DATAPOINT_FIELDS.LBO, "value": 7},
            ]
            for _ in range(100)
        ]
        history = self.simple_create()
        for data_point_info in info:
            data_point = HistoryDataPoint.objects.create(history=history)
            for field_info in data_point_info:
                HistoryDataPointField.objects.create(history_data_point=data_point, **field_info)
        self.assertEqual(history.data_points.count(), len(info))
        target_types = {
            HISTORY_DATAPOINT_FIELDS.AMOUNT: "int",
            HISTORY_DATAPOINT_FIELDS.ASSET: "str",
            HISTORY_DATAPOINT_FIELDS.PRICE: "float",
            HISTORY_DATAPOINT_FIELDS.MBP: "int",
            HISTORY_DATAPOINT_FIELDS.LBO: "int",
        }
        for data_point in history.data_points.all():
            for field in data_point.fields.all():
                self.assertEqual(field.target_type, target_types[field.key])

    def test_invalid_data_point(self):
        history = self.simple_create()
        data_point = HistoryDataPoint.objects.create(history=history)

        with self.assertRaises(HistoryError.InvalidDataPointFieldKey):
            HistoryDataPointField.objects.create(history_data_point=data_point, key="INVALID", value=1)


class HistoryBINANCETestCase(HistoryTestCase, ModelTestCase):
    exchange = "BINANCE"
