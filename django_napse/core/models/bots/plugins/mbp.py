from django_napse.core.models.bots.plugin import Plugin
from django_napse.utils.constants import PLUGIN_CATEGORIES


class MBPPlugin(Plugin):
    @property
    def plugin_category(self):
        return PLUGIN_CATEGORIES.PRE_PROCESSING

    def _apply(self, data: dict) -> dict:
        return super()._apply(data)
