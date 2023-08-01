from django_napse.core.models import EmptyBotConfig, Exchange, ExchangeAccount, NapseSpace, SinglePairArchitechture
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.bots.test_architechture -v2 --keepdb --parallel
"""


class ArchitechtureTestCase:
    def simple_create(self):
        return self.model.objects.create(space=self.space, settings=self.settings)


class SinglePairArchitechtureTestCase(ArchitechtureTestCase, ModelTestCase):
    model = SinglePairArchitechture
