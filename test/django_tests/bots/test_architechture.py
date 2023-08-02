from django_napse.core.models import Controller, SinglePairArchitechture
from django_napse.utils.model_test_case import ModelTestCase

"""
python test/test_app/manage.py test test.django_tests.bots.test_architechture -v2 --keepdb --parallel
"""


class ArchitechtureTestCase:
    model = SinglePairArchitechture

    def simple_create(self):
        return self.model.objects.create(
            controller=Controller.objects.create(
                space=self.space,
                base="BTC",
                quote="USDT",
                interval="1m",
            ),
        )

    def attributes(self):  # pragma: no cover
        error_msg = "attributes not implemented for the Architechture base class, please implement it in the child class."
        raise NotImplementedError(error_msg)


class SinglePairArchitechtureTestCase(ArchitechtureTestCase, ModelTestCase):
    exchange = "BINANCE"
