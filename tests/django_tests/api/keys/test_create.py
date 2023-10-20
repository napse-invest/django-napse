from django_napse.api.keys import KeyView
from django_napse.utils.api_test_case import APITestCase
from django_napse.utils.dict_comparison import compare_responses

"""
python tests/test_app/manage.py test tests.django_tests.api.keys.test_create -v2 --keepdb --parallel
"""


class KeyCreateAPITestCase:
    def test_create(self):
        self.run_tests("create")

    def setup(self):
        def create_all_good():
            def setup__create():
                return self.client.post(path=self.url, data=self.data, headers=self.headers)

            def check__create(response):
                return compare_responses(response.data, {"key": ""})

            return {
                "name": "create_all_good",
                "setup": setup__create,
                "status_code": 201,
                "checks": [check__create],
            }

        def create_missing_username():
            def setup__create():
                return self.client.post(path=self.url, data={}, headers=self.headers)

            def check__create(response):
                return compare_responses(response.data, {"error": ""})

            return {
                "name": "create_missing_username",
                "setup": setup__create,
                "status_code": 400,
                "data": {},
                "checks": [check__create],
            }

        return {
            "create": {
                "url_name": "key-list",
                "view": KeyView,
                "method": "POST",
                "data": {"username": "test_username"},
                "tests": [
                    # create_all_good(),
                    # create_missing_username(),
                ],
            },
        }


class KeyCreateAPIBinanceTestCase(KeyCreateAPITestCase, APITestCase):
    exchange = "BINANCE"
