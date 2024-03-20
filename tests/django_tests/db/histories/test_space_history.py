from django_napse.core.models import SpaceHistory
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.db.histories -v2 --keepdb --parallel
"""


class SpaceHistoryTestCase:
    model = SpaceHistory

    def simple_create(self):
        return self.model.objects.create(owner=self.space)

    def test_owner(self):
        self.assertEqual(self.simple_create().owner, self.space)

    def test_get_or_create(self):
        history1 = self.model.get_or_create(self.space)
        history2 = self.model.get_or_create(self.space)
        self.assertEqual(history1, history2)


class SpaceHistoryBINANCETestCase(SpaceHistoryTestCase, ModelTestCase):
    exchange = "BINANCE"
