from django.db import models

from django_napse.utils.findable_class import FindableClass


class Architechture(models.Model, FindableClass):
    def __str__(self) -> str:
        return f"ARCHITECHTURE {self.pk}"

    def get_candles(self):  # pragma: no cover
        error_msg = "get_candles not implemented for the Architechture base class, please implement it in the child class."
        raise NotImplementedError(error_msg)

    def trigger_actions(self, bot, connections, strategy=None):
        strategy = strategy or bot.strategy.find()
        candles = self.get_candles()
        pre_strategy_data_plugin_data = {}
        for plugin in strategy.plugins:
            result = plugin.apply_pre_strategy()
            if result is not None:
                pre_strategy_data_plugin_data[plugin.name] = result

        all_orders = []
        all_modifications = []
        for connection in connections:
            orders, modifications = strategy.give_order(
                data={
                    "candles": candles,
                    "connection": connection,
                    "pre_strategy_data_plugin_data": pre_strategy_data_plugin_data,
                },
            )
            all_orders += orders
            all_modifications += modifications
        return all_orders, all_modifications
