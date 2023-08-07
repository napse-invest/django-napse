from django.test import TestCase

from django_napse.core.models import EXCHANGE_ACCOUNT_DICT, NapseSpace
from django_napse.core.settings import napse_settings


class ModelTestCase(TestCase):
    model = None
    exchange = None

    def skip_condition(self):
        if self.__class__.__name__ == "ModelTestCase":
            return True, "because ModelTestCase (base class) tests shouldn't be run."
        if not self.__class__.__name__.endswith(f"{self.exchange}TestCase"):
            error_msg = f"ModelTestCase subclass {self.__class__.__name__} name must end with <Exchange>TestCase."
            error_msg += " Make sure you are writing tests as specified in the docs."
        if self.exchange is not None and self.exchange not in napse_settings.NAPSE_EXCHANGES_TO_TEST:
            return True, f"because {self.exchange} is not in {napse_settings.NAPSE_EXCHANGES_TO_TEST}"
        return False, ""

    def simple_create(self):
        error_msg = "You must define a simple_create method."
        raise NotImplementedError(error_msg)

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
            return NapseSpace.objects.get(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")
        except NapseSpace.DoesNotExist:
            return NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")

    def test_setup(self):
        skip, reason = self.skip_condition()
        if skip:
            self.skipTest(reason)
        if self.model is None:
            error_msg = f"ModelTestCase subclass {self.__class__.__name__} must define a model attribute."
            raise NotImplementedError(error_msg)

    def test_simple_creation(self):
        skip, reason = self.skip_condition()
        if skip:
            self.skipTest(reason)
        instance = self.simple_create()
        if instance is None:
            error_msg = "simple_create method must return the created instance."
            raise ValueError(error_msg)

    def test_info(self):
        skip, reason = self.skip_condition()
        if skip:
            self.skipTest(reason)
        instance = self.simple_create()
        instance.info(verbose=False)

    def test_str(self):
        skip, reason = self.skip_condition()
        if skip:
            self.skipTest(reason)
        instance = self.simple_create()
        instance.__str__()
