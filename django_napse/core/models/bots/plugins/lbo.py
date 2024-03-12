from django_napse.core.models.bots.plugin import Plugin
from django_napse.core.models.connections.connection import ConnectionSpecificArgs
from django_napse.utils.constants import PLUGIN_CATEGORIES, SIDES


class LBOPlugin(Plugin):
    @classmethod
    def plugin_category(cls):
        return PLUGIN_CATEGORIES.POST_ORDER

    def apply__no_db(self, data: dict) -> dict:
        order = data["order"]
        if order["side"] == SIDES.BUY:
            order["ConnectionModifications"] += [
                {
                    "key": "lbo",
                    "value": data["connection_data"][data["connection"]]["connection_specific_args"]["lbo"].get_value() + 1,
                    "target_type": "int",
                    "ignore_failed_order": False,
                    "connection_specific_arg": data["connection_data"][data["connection"]]["connection_specific_args"]["lbo"],
                },
            ]
        if order["side"] == SIDES.SELL:
            order["ConnectionModifications"] += [
                {
                    "key": "lbo",
                    "value": 0,
                    "target_type": "int",
                    "ignore_failed_order": False,
                    "connection_specific_arg": data["connection_data"][data["connection"]]["connection_specific_args"]["lbo"],
                },
            ]
        return data

    def _connect(self, connection):
        ConnectionSpecificArgs.objects.create(connection=connection, key="lbo", value="0", target_type="int")
