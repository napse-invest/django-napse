from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


class CustomTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.custom_params(modes=None)

    def custom_params(self, modes):
        self.modes = modes
        self.additional_params()

    def additional_params(self):
        pass

    def request(self, method):
        match method:
            case "GET":
                return self.client.get(self.url)
            case "POST":
                return self.client.post(self.url)
            case "PUT":
                return self.client.put(self.url)
            case "PATCH":
                return self.client.patch(self.url)
            case "DELETE":
                return self.client.delete(self.url)
            case _:
                error_msg = f"Unknown method: {method}"
                raise ValueError(error_msg)

    def run_tests(self, mode):
        if mode not in self.modes:
            error_msg = f"Unknown mode: {mode}"
            raise ValueError(error_msg)

        error_list = []

        self.url = reverse(self.modes[mode]["url_name"], kwargs={"pk": 1} if self.modes[mode]["method"] in ["PATCH", "PUT", "DELETE"] else {})
        self.url_name = self.modes[mode]["url_name"]

        if self.modes[mode]["permissions"] == []:
            response = self.request(self.modes[mode]["method"])
            try:
                self.assertEqual(response.status_code, 200)
            except Exception as e:
                e.add_note("No permissions test failed (no permissions didn't return 200)")
                error_list.append(e)
        else:
            if "IsActive" in self.modes[mode]["permissions"]:
                response = self.request(self.modes[mode]["method"])
                try:
                    self.assertEqual(response.status_code, 401)
                except Exception as e:
                    e.add_note("IsAuthenticated test failed (no permissions didn't return 401)")
                    error_list.append(e)
            if "IsAuthenticated" in self.modes[mode]["permissions"]:
                response = self.request(self.modes[mode]["method"])
                try:
                    self.assertEqual(response.status_code, 401)
                except Exception as e:
                    e.add_note("IsAuthenticated test failed (no permissions didn't return 401)")
                    error_list.append(e)

            if "IsActive" in self.modes[mode]["permissions"]:
                self.user.is_active = True
                self.user.save()

            if "IsAuthenticated" in self.modes[mode]["permissions"]:
                self.client.force_authenticate(user=self.user)

        for test in self.modes[mode]["tests"]:
            response = test["setup_function"]()
            try:
                self.assertEqual(test["awaited_status_code"], response.status_code)
            except Exception as e:
                e.add_note(f"Test: {test['setup_function'].__name__} | status code")
                error_list.append(e)

            for check in test["checks"]:
                try:
                    self.assertTrue(check(response))
                except Exception as e:
                    e.add_note(f"Test: {test['setup_function'].__name__} | check {check.__name__}")
                    error_list.append(e)

        if len(error_list) > 0:
            error_msg = f"Errors in {mode} mode"
            raise ExceptionGroup(error_msg, error_list)
