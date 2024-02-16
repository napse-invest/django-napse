from contextlib import suppress

from django.test import TestCase

from django_napse.core.settings import napse_settings
from django_napse.utils.model_test_case import ModelTestCase

"""
python tests/test_app/manage.py test tests.django_tests.test_validation -v2 --keepdb --parallel
"""


class ValidateModelTestCaseSubclassesTestCase(TestCase):
    def test_naming_convention(self):
        for subclass in ModelTestCase.__subclasses__():
            if not subclass.__name__.endswith("TestCase"):
                error_msg = f"ModelTestCase subclass {subclass.__name__} name must end with TestCase."
                error_msg += " Make sure you are writing tests as specified in the docs."
                raise ValueError(error_msg)

    def test_all_exchanges_are_tested(self):
        all_tests = {}
        for subclass in ModelTestCase.__subclasses__():
            with suppress(AttributeError):
                if subclass.skip_exchange_validation:
                    continue
            if subclass.exchange is None:
                error_msg = f"ModelTestCase subclass {subclass.__name__} must have an exchange attribute."
                error_msg += " Make sure you are writing tests as specified in the docs."
                raise ValueError(error_msg)

            if subclass.__name__.endswith(f"{subclass.exchange}TestCase"):
                subclass_name = subclass.__name__.replace(f"{subclass.exchange}TestCase", "")
                all_tests[subclass_name] = [*all_tests.get(subclass_name, []), subclass.exchange]

            else:
                error_msg = f"ModelTestCase subclass {subclass.__name__} must end with <Exchange>TestCase."
                error_msg += " Make sure you are writing tests as specified in the docs."
                raise ValueError(error_msg)

        for subclass_name, exchanges in all_tests.items():
            if exchanges != napse_settings.NAPSE_EXCHANGES_TO_TEST:
                print(exchanges, napse_settings.NAPSE_EXCHANGES_TO_TEST)
                diff = [exchange for exchange in napse_settings.NAPSE_EXCHANGES_TO_TEST if exchange not in exchanges]
                error_msg = f"ModelTestCase subclass {subclass_name} is missing tests for exchanges {diff}"
                raise ValueError(error_msg)
