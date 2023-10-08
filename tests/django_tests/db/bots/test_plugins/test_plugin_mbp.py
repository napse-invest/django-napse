from django_napse.core.models import MBPPlugin
from django_napse.utils.constants import PLUGIN_CATEGORIES
from django_napse.utils.model_test_case import ModelTestCase
from tests.django_tests.db.bots.test_plugin import PluginDefaultTestCase

"""
python tests/test_app/manage.py test tests.django_tests.bots.test_plugin_mbp -v2 --keepdb --parallel
"""


class MBPPluginTestCase(PluginDefaultTestCase):
    model = MBPPlugin

    def test_plugin_category(self):
        plugin = self.simple_create()
        self.assertEqual(plugin.plugin_category(), PLUGIN_CATEGORIES.POST_ORDER)


class MBPPluginBINANCETestCase(MBPPluginTestCase, ModelTestCase):
    exchange = "BINANCE"
