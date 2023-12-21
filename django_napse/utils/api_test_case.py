from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_api_key.permissions import HasAPIKey

from django_napse.api.custom_permissions import HasAdminPermission, HasFullAccessPermission, HasMasterKey, HasReadPermission, HasSpace
from django_napse.auth.models import KeyPermission
from django_napse.auth.models.keys.key import NapseAPIKey
from django_napse.utils.constants import PERMISSION_TYPES
from django_napse.utils.custom_test_case import CustomTestCase


class APITestCase(CustomTestCase):
    def setUp(self):
        self.client = APIClient()
        self.modes = self.setup()
        if self.modes == {} or not isinstance(self.modes, dict):
            error_msg = "Modes not defined"
            raise ValueError(error_msg)

    def setup(self):
        error_msg = "Setup function not implemented"
        raise NotImplementedError(error_msg)

    def build_url(self, kwargs=None):
        if kwargs and kwargs.get("pk", None):
            self.url = reverse(viewname=self.url_name, kwargs={"pk": kwargs.pop("pk")})
        else:
            self.url = reverse(viewname=self.url_name)
        if kwargs:
            self.url += "?" + "&".join([f"{key}={value}" for key, value in kwargs.items()])

    def build_key(self, permissions):
        key_obj, self.key = NapseAPIKey.objects.create_key(name="test")
        if HasReadPermission in permissions:
            KeyPermission.objects.create(key=key_obj, space=self.space, permission_type=PERMISSION_TYPES.READ_ONLY, approved=True)
        if HasFullAccessPermission in permissions:
            KeyPermission.objects.create(key=key_obj, space=self.space, permission_type=PERMISSION_TYPES.FULL_ACCESS, approved=True)
        if HasAdminPermission in permissions:
            KeyPermission.objects.create(key=key_obj, space=self.space, permission_type=PERMISSION_TYPES.ADMIN, approved=True)

    def authenticate(self):
        self.headers["Authorization"] = f"Api-Key {self.key}"

    def logout(self):
        self.headers.pop("Authorization")

    def request(self, method):
        match method:
            case "GET":
                return self.client.get(path=self.url, data=self.data, headers=self.headers)
            case "POST":
                return self.client.post(path=self.url, data=self.data, headers=self.headers)
            case "PUT":
                return self.client.put(path=self.url, data=self.data, headers=self.headers)
            case "PATCH":
                return self.client.patch(path=self.url, data=self.data, headers=self.headers)
            case "DELETE":
                return self.client.delete(path=self.url, data=self.data, headers=self.headers)
            case _:
                error_msg = f"Unknown method: {method}"
                raise ValueError(error_msg)

    def check_auth(self, name: str, mode: str, error_list: list, divider: int = 1, expected: int = 403) -> None:
        response = self.request(self.modes[mode]["method"])
        try:
            self.assertEqual(response.status_code // divider, expected)
        except AssertionError as e:
            e.add_note(f"{name} test failed (no permissions didn't return 403)")
            e.add_note(str(response.data))
            error_list.append(e)

    def run_tests(self, mode):
        if mode not in self.modes:
            error_msg = f"Unknown mode: {mode}"
            raise ValueError(error_msg)

        error_list = []
        self.kwargs = self.modes[mode].get("kwargs", {})
        self.data = self.modes[mode].get("data", {})
        self.headers = self.modes[mode].get("headers", {})
        self.url_name = self.modes[mode]["url_name"]
        self.build_url(kwargs={"pk": 1} if self.modes[mode]["method"] in ["PATCH", "PUT", "DELETE"] and not self.kwargs else self.kwargs)

        permissions = self.modes[mode]["view"].permission_classes
        permission_importance = {
            HasSpace: 0,
            HasAPIKey: 1,
            HasReadPermission: 2,
            HasFullAccessPermission: 3,
            HasAdminPermission: 4,
            HasMasterKey: 5,
        }
        permissions.sort(key=lambda x: permission_importance[x])

        if permissions == []:
            self.check_auth(name="No permissions", mode=mode, error_list=error_list, divider=100, expected=2)
        else:
            if HasSpace in permissions:
                self.check_auth(name="HasSpace with no key", mode=mode, error_list=error_list, expected=400)
                self.build_url(kwargs={"space": str("random uuid"), **self.kwargs})
                self.check_auth(name="HasSpace with no key", mode=mode, error_list=error_list, expected=400)
                self.build_url(kwargs={"space": str("7aafc68d-f619-4874-aaf5-c123a176e303"), **self.kwargs})
                self.check_auth(name="HasSpace with no key", mode=mode, error_list=error_list, expected=400)
                self.build_url(kwargs={"space": str(self.space.uuid), **self.kwargs})

            if HasAPIKey in permissions:
                self.check_auth(name="HasAPIKey with no key", mode=mode, error_list=error_list)

            if HasReadPermission in permissions:
                self.check_auth(name="HasReadPermission with no key", mode=mode, error_list=error_list)
                self.build_key([])
                self.authenticate()
                self.check_auth(name="HasReadPermission with no permissions", mode=mode, error_list=error_list)

            if HasFullAccessPermission in permissions:
                self.check_auth(name="HasFullAccessPermission with no key", mode=mode, error_list=error_list)
                self.build_key([])
                self.authenticate()
                self.check_auth(name="HasFullAccessPermission with no permissions", mode=mode, error_list=error_list)
                self.build_key([HasReadPermission])
                self.authenticate()
                self.check_auth(name="HasFullAccessPermission with read permissions", mode=mode, error_list=error_list)

            if HasAdminPermission in permissions:
                self.check_auth(name="HasAdminPermission with no key", mode=mode, error_list=error_list)
                self.build_key([])
                self.authenticate()
                self.check_auth(name="HasAdminPermission with no permissions", mode=mode, error_list=error_list)
                self.build_key([HasReadPermission])
                self.authenticate()
                self.check_auth(name="HasAdminPermission with read permissions", mode=mode, error_list=error_list)
                self.build_key([HasReadPermission, HasFullAccessPermission])
                self.authenticate()
                self.check_auth(name="HasAdminPermission with read and full access permissions", mode=mode, error_list=error_list)

        self.build_key(permissions)
        self.authenticate()

        for test in self.modes[mode]["tests"]:
            response = test["setup"]()
            try:
                self.assertEqual(test["status_code"], response.status_code)
            except AssertionError as e:
                e.add_note(f"Test: {test['name']} | {test['setup'].__name__} | status code")
                e.add_note(str(response.data))
                error_list.append(e)

            for check in test["checks"]:
                try:
                    self.assertTrue(check(response))
                except Exception as e:
                    e.add_note(f"Test: {test['name']} | {test['setup'].__name__} | check {check.__name__}")
                    e.add_note(str(response.data))
                    error_list.append(e)

        if len(error_list) > 0:
            error_msg = f"Errors in {mode} mode"
            raise ExceptionGroup(error_msg, error_list)


class ViewTest:
    def __init__(self, testcase_instance: APITestCase, *args, **kwargs):
        self.testcase_instance = testcase_instance

    def setup(self, data: dict | None = None):
        def _setup(data=data):
            # TODO: Add other methods (post, put, patch, delete)
            return self.testcase_instance.client.get(
                path=self.testcase_instance.url,
                data=data,
                headers=self.testcase_instance.headers,
            )

        return _setup

    def run(self) -> list[dict[str, any]]:
        raise NotImplementedError
