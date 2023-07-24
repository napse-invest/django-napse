from django.db import models

from django_napse.utils.findable_class import FindableClass


class Architechture(models.Model, FindableClass):
    def __str__(self) -> str:
        return f"ARCHITECHTURE {self.pk}"

    def get_candles(self):
        error_msg = "get_candles not implemented for the Architechture base class, please implement it in the child class."
        raise NotImplementedError(error_msg)

    def trigger_actions(self, bot, connections):
        candles = self.get_candles()

        pre_strategy_data_plugin_data = {}
        for plugin in bot.strategy.plugins:
            result = plugin.apply_pre_strategy()
            if result is not None:
                pre_strategy_data_plugin_data[plugin.name] = result

        all_orders = []
        all_modifications = []
        for connection in connections:
            orders, modifications = bot.strategy.find().give_order(
                data={
                    "candles": candles,
                    "connection": connection,
                    "pre_strategy_data_plugin_data": pre_strategy_data_plugin_data,
                },
            )
            all_orders += orders
            all_modifications += modifications
        return all_orders, all_modifications
