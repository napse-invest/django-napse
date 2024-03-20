from django.test import TestCase

from django_napse.core.models import EXCHANGE_ACCOUNT_DICT, Space
from django_napse.core.settings import napse_settings


class CustomTestCase(TestCase):
    exchange = None

    def skip_condition(self):
        if self.__class__.__name__ == "ModelTestCase":
            return True, "because ModelTestCase (base class) tests shouldn't be run."
        if self.__class__.__name__ == "APITestCase":
            return True, "because ModelTestCase (base class) tests shouldn't be run."

        if not self.__class__.__name__.endswith(f"{self.exchange}TestCase"):
            error_msg = f"CustomTestCase subclass {self.__class__.__name__} name must end with <Exchange>TestCase."
            error_msg += " Make sure you are writing tests as specified in the docs."
        if self.exchange is not None and self.exchange not in napse_settings.NAPSE_EXCHANGES_TO_TEST:
            return True, f"because {self.exchange} is not in {napse_settings.NAPSE_EXCHANGES_TO_TEST}"
        return False, ""

    @property
    def exchange_account(self):
        try:
            return EXCHANGE_ACCOUNT_DICT[self.exchange].objects.get(name=f"{self.exchange} Test Account")
        except KeyError as e:
            error_msg = f"Exchange {self.exchange} isn't a valid choice."
            raise ValueError(error_msg) from e

    @property
    def space(self):
        try:
            return Space.objects.get(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")
        except Space.DoesNotExist:
            return Space.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")
