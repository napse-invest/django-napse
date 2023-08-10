from django.db import models

from django_napse.utils.findable_class import FindableClass


class Architecture(models.Model, FindableClass):
    def __str__(self) -> str:
        return f"ARCHITECHTURE {self.pk}"

    def get_candles(self):  # pragma: no cover
        error_msg = "get_candles not implemented for the Architecture base class, please implement it in the child class."
        raise NotImplementedError(error_msg)

    def copy(self):
        error_msg = "copy not implemented for the Architecture base class, please implement it in the child class."
        raise NotImplementedError(error_msg)

    def list_controllers(self):
        error_msg = "list_controllers not implemented for the Architecture base class, please implement it in the child class."
        raise NotImplementedError(error_msg)

    def prepare_data(self):
        return {"candles": self.get_candles()}

    def trigger_actions(self, connections, data: dict):
        strategy = self.strategy.find()

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
                    "candles": data.pop("candles"),
                    "connection": connection,
                    "pre_strategy_data_plugin_data": pre_strategy_data_plugin_data,
                },
            )
            all_orders += orders
            all_modifications += modifications
        return all_orders, all_modifications
