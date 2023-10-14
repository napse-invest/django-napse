from django_napse.api.spaces import SpaceView
from django_napse.utils.api_test_case import APITestCase

# from django_napse.utils.dict_comparison import compare_responses

"""
python tests.test_app.manage.py test tests.django_tests.api.spaces.test_spaces_view -v2 --keepdb --parallel
"""


class SpaceViewTestCase:
    def test_list(self):
        self.run_tests("list")

    def test_retrieve(self):
        self.run_tests("retrieve")

    def test_create(self):
        self.run_tests("create")

    def setup(self):
        return {
            "list": {
                "url_name": "space-list",
                "view": SpaceView,
                "method": "GET",
                "data": {"pk": self.space.id},
                "tests": [],
            },
            "retrieve": {
                "url_name": "space-detail",
                "view": SpaceView,
                "method": "GET",
                "data": {"pk": self.space.id},
                "tests": [],
            },
            "create": {
                "url_name": "space-list",
                "view": SpaceView,
                "method": "POST",
                "data": {"pk": self.space.id},
                "tests": [],
            },
        }


class SpaceViewAPIBinanceTestCase(SpaceViewTestCase, APITestCase):
    exchange = "BINANCE"
