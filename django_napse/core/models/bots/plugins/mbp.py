from django_napse.core.models.bots.plugin import Plugin
from django_napse.core.models.connections.connection import ConnectionSpecificArgs
from django_napse.utils.constants import PLUGIN_CATEGORIES, SIDES


class MBPPlugin(Plugin):
    @classmethod
    def plugin_category(cls):
        return PLUGIN_CATEGORIES.POST_ORDER

    def apply__no_db(self, data: dict) -> dict:
        order = data["order"]
        if order["side"] == SIDES.BUY:
            new_mbp = f"{order['controller'].base}|{order['price']}"
            order["ConnectionModifications"] += [
                {
                    "key": "mbp",
                    "value": new_mbp,
                    "target_type": "plugin_mbp",
                    "ignore_failed_order": False,
                    "connection_specific_arg": data["connection_data"][data["connection"]]["connection_specific_args"]["mbp"],
                },
            ]
        return data

    def _connect(self, connection):
        ConnectionSpecificArgs.objects.create(connection=connection, key="mbp", value="None", target_type="float")
