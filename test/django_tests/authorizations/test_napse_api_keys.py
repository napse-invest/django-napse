from django.db.utils import IntegrityError

from django_napse.core.models import NapseAPIKey
from django_napse.utils.model_test_case import ModelTestCase


class NapseAPIKeyTestCase:
    model = NapseAPIKey

    def simple_create(self):
        return NapseAPIKey.objects.create(name="Test API Key", description="This is a test API key")

    def test_api_key_duplicate_name(self):
        NapseAPIKey.objects.create(name="Test API Key", description="This is a test API key")
        with self.assertRaises(IntegrityError):
            NapseAPIKey.objects.create(name="Test API Key", description="This is a test API key")

    def test_api_key_duplicate_key(self):
        key1 = NapseAPIKey.objects.create(name="Test API Key", description="This is a test API key")
        key2 = NapseAPIKey.objects.create(name="Test API Key 2", description="This is a test API key")
        key2.napse_API_key = key1.napse_API_key
        with self.assertRaises(IntegrityError):
            key2.save()


class NapseAPIKeyBINANCETestCase(NapseAPIKeyTestCase, ModelTestCase):
    exchange = "BINANCE"
