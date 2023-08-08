from django_napse.core.models import Controller, SinglePairArchitechture
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.bots.test_architechture -v2 --keepdb --parallel
"""


class ArchitechtureTestCase:
    model = SinglePairArchitechture

    def simple_create(self):
        return self.model.objects.create(
            controller=Controller.get(
                space=self.space,
                base="BTC",
                quote="USDT",
                interval="1m",
            ),
        )


class SinglePairArchitechtureBINANCETestCase(ArchitechtureTestCase, ModelTestCase):
    exchange = "BINANCE"
