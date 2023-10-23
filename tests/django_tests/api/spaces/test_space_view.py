import contextlib

from django_napse.api.spaces import SpaceView
from django_napse.utils.api_test_case import APITestCase, ViewTest
from django_napse.utils.dict_comparison import compare_responses

"""
python tests/test_app/manage.py test tests.django_tests.api.spaces.test_space_view -v2 --keepdb --parallel
"""


class ListSpaceViewTest(ViewTest):
    def check_response(self, response) -> bool:
        return compare_responses(
            response.data[0],
            {
                "name": str(),
                "description": str(),
                "uuid": str(),
                "delta": float(),
                "value": float(),
                "exchange_account": str(),
            },
        )

    def run(self):
        return [
            {
                "name": "response",
                "setup": self.setup(data=None),
                "status_code": 200,
                "checks": [self.check_response],
            },
        ]


class RetrieveSpaceViewTest(ViewTest):
    def check_response(self, response) -> bool:
        return compare_responses(
            response.data,
            {
                "name": str(),
                "description": str(),
                "uuid": str(),
                "exchange_account": str(),
                "created_at": str(),
                "statistics": {
                    "value": float(),
                    "order_count_30": float(),
                    "delta_30": float(),
                },
                "wallet": {},
                "history": [],
                "fleets": [],
            },
            authorize_abstract_comparison=True,
        )

    def run(self):
        return [
            {
                "name": "missing_data",
                "setup": self.setup(),
                "status_code": 200,
                "checks": [self.check_response],
            },
        ]


class SpaceViewTestCase:
    # def test_list(self):
    #     self.run_tests("list")

    # def test_retrieve(self):
    #     self.run_tests("retrieve")

    def setUp(self):
        super().setUp()
        from django_napse.core.models import SpaceHistory

        with contextlib.suppress(Exception):
            SpaceHistory.objects.create(owner=self.space)

    def setup(self):
        list_test = ListSpaceViewTest(self)
        retrieve_test = RetrieveSpaceViewTest(self)

        return {
            "list": {
                "url_name": "space-list",
                "view": SpaceView,
                "method": "GET",
                "tests": list_test.run(),
            },
            "retrieve": {
                "url_name": "space-detail",
                "view": SpaceView,
                "method": "GET",
                "kwargs": {"pk": self.space.uuid},
                "tests": retrieve_test.run(),
            },
        }


class SpaceViewAPIBinanceTestCase(SpaceViewTestCase, APITestCase):
    exchange = "BINANCE"
