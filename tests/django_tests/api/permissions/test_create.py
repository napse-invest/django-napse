from django_napse.api.permissions import Permission
from django_napse.utils.api_test_case import APITestCase
from django_napse.utils.dict_comparison import compare_responses

"""
python tests/test_app/manage.py test tests.django_tests.api.permissions.create -v2 --keepdb --parallel
"""


class PermissionCreateTestCase:
    def test_create(self):
        self.run_tests("create")

    def setup(self):
        def create_all_good():
            def setup__create():
                return self.client.post(path=self.url, data={"permission_type": "READ_ONLY"}, headers=self.headers)

            def check__create(response):
                return compare_responses(response.data, None)

            return {
                "name": "create_all_good",
                "setup": setup__create,
                "status_code": 201,
                "checks": [check__create],
            }

        def missing_permission_type():
            def setup__create():
                return self.client.post(path=self.url, data={}, headers=self.headers)

            def check__create(response):
                return compare_responses(response.data, {"error": ""})

            return {
                "name": "missing_permission_type",
                "setup": setup__create,
                "status_code": 400,
                "checks": [check__create],
            }

        def invalid_permission_type():
            def setup__create():
                return self.client.post(path=self.url, data={"permission_type": "INVALID"}, headers=self.headers)

            def check__create(response):
                return compare_responses(response.data, {"error": ""})

            return {
                "name": "invalid_permission_type",
                "setup": setup__create,
                "status_code": 400,
                "checks": [check__create],
            }

        def duplicate_permission():
            def setup__create():
                return self.client.post(path=self.url, data={"permission_type": "READ_ONLY"}, headers=self.headers)

            def check__create(response):
                return compare_responses(response.data, {"error": ""})

            return {
                "name": "duplicate_permission",
                "setup": setup__create,
                "status_code": 400,
                "checks": [check__create],
            }

        return {
            "create": {
                "url_name": "permission-list",
                "view": Permission,
                "method": "POST",
                "tests": [
                    create_all_good(),
                    missing_permission_type(),
                    invalid_permission_type(),
                    duplicate_permission(),
                ],
            },
        }


class PermissionCreateAPIBinanceTestCase(PermissionCreateTestCase, APITestCase):
    exchange = "BINANCE"
