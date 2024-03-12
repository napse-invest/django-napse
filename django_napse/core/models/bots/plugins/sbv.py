from django_napse.core.models.bots.plugin import Plugin
from django_napse.core.models.connections.connection import ConnectionSpecificArgs
from django_napse.core.models.wallets.currency import CurrencyPydantic
from django_napse.utils.constants import PLUGIN_CATEGORIES, SIDES


class SBVPlugin(Plugin):
    @classmethod
    def plugin_category(cls):
        return PLUGIN_CATEGORIES.POST_ORDER

    def apply__no_db(self, data: dict) -> dict:
        order = data["order"]
        current_base_amout = (
            data["connection_data"][data["connection"]]["wallet"]
            .currencies.get(order["controller"].base, CurrencyPydantic(ticker=order["controller"].base, amount=0, mbp=0))
            .amount
        )
        current_quote_amout = (
            data["connection_data"][data["connection"]]["wallet"]
            .currencies.get(order["controller"].quote, CurrencyPydantic(ticker=order["controller"].quote, amount=0, mbp=0))
            .amount
        )
        if data["connection_data"][data["connection"]]["connection_specific_args"]["sbv"].get_value() is None or order["side"] == SIDES.SELL:
            order["ConnectionModifications"] += [
                {
                    "key": "sbv",
                    "value": current_quote_amout + current_base_amout * order["price"],
                    "target_type": "float",
                    "ignore_failed_order": False,
                    "connection_specific_arg": data["connection_data"][data["connection"]]["connection_specific_args"]["sbv"],
                },
            ]
        return data

    def _connect(self, connection):
        ConnectionSpecificArgs.objects.create(connection=connection, key="sbv", value="None", target_type="float")
