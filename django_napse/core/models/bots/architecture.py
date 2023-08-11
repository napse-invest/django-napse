from typing import Optional

from django.db import models

from django_napse.utils.constants import ORDER_LEEWAY_PERCENTAGE, SIDES
from django_napse.utils.errors.orders import OrderError
from django_napse.utils.findable_class import FindableClass


class Architecture(models.Model, FindableClass):
    def __str__(self) -> str:
        return f"ARCHITECHTURE {self.pk}"

    def get_candles(self):  # pragma: no cover
        if self.__class__ == Architecture:
            error_msg = "get_candles not implemented for the Architecture base class, please implement it in a subclass."
        else:
            error_msg = f"get_candles not implemented for the Architecture base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def get_extras(self):  # pragma: no cover
        if self.__class__ == Architecture:
            error_msg = "get_extras not implemented for the Architecture base class, please implement it in a subclass."
        else:
            error_msg = f"get_extras not implemented for the Architecture base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def copy(self):  # pragma: no cover
        if self.__class__ == Architecture:
            error_msg = "copy not implemented for the Architecture base class, please implement it in a subclass."
        else:
            error_msg = f"copy not implemented for the Architecture base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def list_controllers(self):  # pragma: no cover
        if self.__class__ == Architecture:
            error_msg = "list_controllers not implemented for the Architecture base class, please implement it in a subclass."
        else:
            error_msg = f"list_controllers not implemented for the Architecture base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def prepare_data(self):
        return {
            "candles": {controller: self.get_candles(controller) for controller in self.list_controllers()},
            "extras": {},
        }

    def prepare_db_data(self):
        return {
            "strategy": self.strategy.find(),
            "architecture": self.find(),
            "controllers": self.list_controllers(),
            "connections": self.strategy.bot.get_connections(),
            "connection_data": self.strategy.bot.get_connection_data(),
            # "plugins": self.plugins.all(),
        }

    def _get_orders(self, data: dict, no_db_data: Optional[dict] = None) -> list[dict]:
        data = data or self.prepare_data()
        no_db_data = no_db_data or self.prepare_db_data()

        strategy = no_db_data["strategy"]
        connections = no_db_data["connections"]

        all_orders = []
        for connection in connections:
            orders = strategy.give_order(
                data={
                    **data,
                    **no_db_data,
                    "connection": connection,
                },
            )
            required_amount = {}
            for order in orders:
                required_amount[order["asked_for_ticker"]] = required_amount.get(order["asked_for_ticker"], 0) + order["asked_for_amount"]

                if order["side"] == SIDES.KEEP and order["asked_for_amount"] != 0:
                    error_msg = f"Order on {order['pair']} has a side of KEEP but an amount of {order['asked_for_amount']}."
                    raise OrderError.ProcessError(error_msg)
                if order["side"] != SIDES.KEEP and order["asked_for_amount"] == 0:
                    error_msg = f"Order on {order['pair']} has a side of {order['side']} but an amount of 0."
                    raise OrderError.ProcessError(error_msg)

            for ticker, amount in required_amount.items():
                if amount > no_db_data["connection_data"][connection]["wallet"]["currencies"][ticker]["amount"] / (
                    1 + (ORDER_LEEWAY_PERCENTAGE + 1) / 100
                ):
                    available = no_db_data["connection_data"][connection]["wallet"]["currencies"][ticker]["amount"] / (
                        1 + (ORDER_LEEWAY_PERCENTAGE + 1) / 100
                    )
                    for order in [_order for _order in orders if order["asked_for_ticker"] == ticker]:
                        order["asked_for_amount"] *= available / amount
            all_orders += orders
        return all_orders
