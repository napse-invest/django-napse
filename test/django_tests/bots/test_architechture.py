from django_napse.core.models import Controller, SinglePairArchitecture
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.bots.test_architecture -v2 --keepdb --parallel
"""


class ArchitectureTestCase:
    model = SinglePairArchitecture

    def simple_create(self):
        return self.model.objects.create(
            controller=Controller.get(
                space=self.space,
                base="BTC",
                quote="USDT",
                interval="1m",
            ),
        )


class SinglePairArchitectureBINANCETestCase(ArchitectureTestCase, ModelTestCase):
    exchange = "BINANCE"
