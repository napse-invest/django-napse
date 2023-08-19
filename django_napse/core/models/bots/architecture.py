from typing import Optional

from django.db import models

from django_napse.core.models.bots.managers import ArchitectureManager
from django_napse.core.models.bots.strategy import Strategy
from django_napse.utils.constants import ORDER_LEEWAY_PERCENTAGE, PLUGIN_CATEGORIES, SIDES
from django_napse.utils.errors.orders import OrderError
from django_napse.utils.findable_class import FindableClass


class Architecture(models.Model, FindableClass):
    objects = ArchitectureManager()

    def __str__(self) -> str:
        return f"ARCHITECHTURE {self.pk}"

    @property
    def variables(self):
        self = self.find(self.pk)
        variables = {}
        for variable in self._meta.get_fields():
            if variable.name.startswith("variable_"):
                variables[variable.name[8:]] = getattr(self, variable.name)
        return variables

    @property
    def strategy(self):
        return Strategy.objects.get(architecture=self).find()

    def get_candles(self):  # pragma: no cover
        if self.__class__ == Architecture:
            error_msg = "get_candles not implemented for the Architecture base class, please implement it in a subclass."
        else:
            error_msg = f"get_candles not implemented for the Architecture base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def copy(self):  # pragma: no cover
        if self.__class__ == Architecture:
            error_msg = "copy not implemented for the Architecture base class, please implement it in a subclass."
        else:
            error_msg = f"copy not implemented for the Architecture base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def controllers_dict(self):  # pragma: no cover
        if self.__class__ == Architecture:
            error_msg = "controllers_dict not implemented for the Architecture base class, please implement it in a subclass."
        else:
            error_msg = f"controllers_dict not implemented for the Architecture base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def accepted_tickers(self):  # pragma: no cover
        if self.__class__ == Architecture:
            error_msg = "accepted_tickers not implemented for the Architecture base class, please implement it in a subclass."
        else:
            error_msg = f"accepted_tickers not implemented for the Architecture base class, please implement it in the {self.__class__} class."
        raise NotImplementedError(error_msg)

    def accepted_investment_tickers(self):  # pragma: no cover
        if self.__class__ == Architecture:
            error_msg = "accepted_investment_tickers not implemented for the Architecture base class, please implement it in a subclass."
        else:
            error_msg = (
                f"accepted_investment_tickers not implemented for the Architecture base class, please implement it in the {self.__class__} class."
            )
        raise NotImplementedError(error_msg)

    def get_extras(self):
        return {}

    def skip(self, data: dict) -> bool:
        return False

    def strategy_modifications(self, order: dict, data) -> list[dict]:
        return []

    def connection_modifications(self, order: dict, data) -> list[dict]:
        return []

    def architecture_modifications(self, order: dict, data) -> list[dict]:
        return []

    def prepare_data(self):
        return {
            "candles": {controller: self.get_candles(controller) for controller in self.controllers_dict().values()},
            "extras": self.get_extras(),
        }

    def prepare_db_data(self):
        return {
            "strategy": self.strategy.find(),
            "config": self.strategy.find().config.find().settings,
            "architecture": self.find(),
            "controllers": self.controllers_dict(),
            "connections": self.strategy.bot.get_connections(),
            "connection_data": self.strategy.bot.get_connection_data(),
            "plugins": {category: self.strategy.plugins.filter(category=category) for category in PLUGIN_CATEGORIES},
        }

    def _get_orders(self, data: dict, no_db_data: Optional[dict] = None) -> list[dict]:
        data = data or self.prepare_data()
        no_db_data = no_db_data or self.prepare_db_data()
        strategy = no_db_data["strategy"]
        connections = no_db_data["connections"]
        architecture = no_db_data["architecture"]
        all_orders = []
        for connection in connections:
            new_data = {**data, **no_db_data, "connection": connection}
            # pprint(new_data)
            if architecture.skip(data=new_data):
                continue
            for plugin in no_db_data["plugins"][PLUGIN_CATEGORIES.PRE_ORDER]:
                plugin.apply(data=new_data)
            orders = strategy.give_order(data=new_data)
            for order in orders:
                for plugin in no_db_data["plugins"][PLUGIN_CATEGORIES.POST_ORDER]:
                    plugin.apply(data={**new_data, "order": order})
                order["StrategyModifications"] += architecture.strategy_modifications(order=order, data=new_data)
                order["ConnectionModifications"] += architecture.connection_modifications(order=order, data=new_data)
                order["ArchitectureModifications"] += architecture.architecture_modifications(order=order, data=new_data)
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
                if amount > no_db_data["connection_data"][connection]["wallet"]["currencies"].get(ticker, {"amount": 0})["amount"] / (
                    1 + (ORDER_LEEWAY_PERCENTAGE + 1) / 100
                ):
                    available = no_db_data["connection_data"][connection]["wallet"]["currencies"].get(ticker, {"amount": 0})["amount"] / (
                        1 + (ORDER_LEEWAY_PERCENTAGE + 1) / 100
                    )
                    for order in [_order for _order in orders if _order["asked_for_ticker"] == ticker]:
                        order["asked_for_amount"] *= available / amount
            all_orders += orders
        return all_orders
