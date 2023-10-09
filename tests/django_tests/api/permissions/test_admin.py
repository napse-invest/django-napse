from django_napse.api.permissions import AdminPermission
from django_napse.utils.api_test_case import APITestCase
from django_napse.utils.dict_comparison import compare_responses

"""
python tests/test_app/manage.py test tests.django_tests.api.permissions.create -v2 --keepdb --parallel
"""


class PermissionAdminTestCase:
    def test_create(self):
        self.run_tests("create")

    def setup(self):
        def list_all_good():
            def setup__create():
                return self.client.get(path=self.url, headers=self.headers)

            def check__create(response):
                print(response.data)
                return compare_responses(response.data, [])

            return {
                "name": "list_all_good",
                "setup": setup__create,
                "status_code": 204,
                "checks": [check__create],
            }

        return {
            "create": {
                "url_name": "admin_permission-list",
                "view": AdminPermission,
                "method": "GET",
                "tests": [list_all_good()],
            },
        }


class PermissionCreateAPIBinanceTestCase(PermissionAdminTestCase, APITestCase):
    exchange = "BINANCE"
