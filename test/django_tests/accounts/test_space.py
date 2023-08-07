from django.db.utils import IntegrityError

from django_napse.core.models import NapseSpace
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.accounts.test_space -v2 --keepdb --parallel
"""


class NapseSpaceTestCase:
    model = NapseSpace

    def simple_create(self):
        return NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")

    def test_error_create_napse_space_with_same_name(self):
        NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")
        with self.assertRaises(IntegrityError):
            NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")

    def test_error_create_napse_space_with_same_identifier(self):
        first_space = NapseSpace.objects.create(name="Test Space", exchange_account=self.exchange_account, description="This is a test space")
        second_space = NapseSpace.objects.create(name="Test Space 2", exchange_account=self.exchange_account, description="This is a test space")
        second_space.identifier = first_space.identifier

        with self.assertRaises(IntegrityError):
            second_space.save()


class NaspeSpaceBINANCETestCase(NapseSpaceTestCase, ModelTestCase):
    exchange = "BINANCE"
