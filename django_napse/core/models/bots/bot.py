from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from django.db import models

from django_napse.core.models.connections.connection import Connection
from django_napse.core.models.modifications import ArchitectureModification, ConnectionModification, StrategyModification
from django_napse.core.models.orders.order import Order, OrderBatch
from django_napse.utils.errors import BotError

if TYPE_CHECKING:
    from django_napse.core.models.accounts.exchange import ExchangeAccount
    from django_napse.core.models.accounts.space import Space
    from django_napse.core.models.bots.architecture import Architecture, DataType, DBDataType
    from django_napse.core.models.bots.strategy import Strategy
    from django_napse.core.models.fleets.fleet import Fleet
    from django_napse.core.models.wallets.space_simulation_wallet import SpaceSimulationWallet
    from django_napse.core.models.wallets.space_wallet import SpaceWallet


class Bot(models.Model):
    """A bot makes trading decisions based on a strategy."""

    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    name = models.CharField(max_length=100, default="Bot")

    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    strategy: Strategy = models.OneToOneField("Strategy", on_delete=models.CASCADE, related_name="bot")

    def __str__(self) -> str:
        return f"BOT {self.pk=}"

    def save(self, *args: list, **kwargs: dict) -> None:  # noqa: D102
        if self.is_in_simulation and self.is_in_fleet:
            error_msg = "Bot is in simulation and fleet."
            raise BotError.InvalidSetting(error_msg)
        return super().save(*args, **kwargs)

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}Bot {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.name=}\n"

        string += f"{beacon}Strategy:\n"
        new_beacon = beacon + "\t"
        string += f"{beacon}\t{self.strategy.info(verbose=False, beacon=new_beacon)}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def is_in_simulation(self) -> bool:
        """Return True if the bot is in simulation."""
        return hasattr(self, "simulation")

    @property
    def is_in_fleet(self) -> bool:
        """Return True if the bot is in a fleet."""
        return hasattr(self, "link")

    @property
    def is_templace(self) -> bool:
        """Return True if the bot is used as a template by a cluster."""
        """Is self a template bot of a cluster?"""
        return hasattr(self, "cluster")

    @property
    def is_free(self) -> bool:
        """Return True if the bot is not in a simulation, not in a fleet and not a cluster's template bot."""
        return not self.is_in_simulation and not self.is_in_fleet and not self.is_templace

    @property
    def testing(self) -> bool:
        """Return testing status of the fleet (or True if is_in_simulation)."""
        if self.is_in_simulation:
            return True
        if self.is_in_fleet:
            return self.bot_in_cluster.cluster.fleet.testing
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    @property
    def fleet(self) -> Fleet | None:
        """Return the bot's relative fleet."""
        if self.is_in_fleet:
            return self.link.cluster.fleet
        return None

    @property
    def space(self) -> Space:
        """Return the bot's simulation space.

        Raises:
            BotError.NoSpace: If the bot is in a fleet.
            BotError.InvalidSetting: If the bot is not in simulation or fleet.
        """
        if self.is_in_simulation:
            return self.simulation.space
        if self.is_in_fleet:
            error_msg = "Bot is in a fleet and therefore doesn't have a space."
            raise BotError.NoSpace(error_msg)
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    @property
    def exchange_account(self) -> ExchangeAccount:
        """Return the bot's exchange account.

        Raises:
            BotError.InvalidSetting: If the bot is not in simulation or fleet.
        """
        if self.is_in_simulation:
            return self.simulation.space.exchange_account
        if self.is_in_fleet:
            return self.link.cluster.fleet.exchange_account
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    @property
    def _strategy(self) -> Strategy:
        """Return the bot's strategy."""
        return self.strategy.find()

    @property
    def architecture(self) -> Architecture:
        """Return the bot's strategy's architecture."""
        return self._strategy.architecture.find()

    @property
    def controllers(self) -> dict:
        """Return the controller used by bot's architecture."""
        return self.architecture.controllers_dict()

    @property
    def orders(self) -> list[Order]:
        """Return all orders created by the bot."""
        connections = self.connections.select_related("orders").all()
        return [connection.orders for connection in connections]

    def hibernate(self) -> None:
        """Deactivate the bot from trading."""
        if not self.active:
            error_msg = "Bot is already hibernating."
            raise BotError.InvalidSetting(error_msg)
        self.active = False
        self.save()

    def get_connections(self) -> list[Connection]:
        """Return all connections of the bot."""
        return list(self.connections.all())

    def get_connection_data(self) -> dict[str, dict[str, any]]:
        """Return the data of the bot's connections."""
        return {connection: connection.to_dict() for connection in self.get_connections()}

    def get_orders(self, data: DataType, no_db_data: Optional[DBDataType] = None):
        """Return an order and batches (one for each distinct Controller), based on candles input data and bot's strategy."""
        if not self.active:
            error_msg = "Bot is hibernating."
            raise BotError.InvalidSetting(error_msg)
        orders = self.get_orders__no_db(data=data, no_db_data=no_db_data)
        batches = {}
        order_objects = []
        for order in orders:
            controller = order["controller"]
            batches[controller] = OrderBatch.objects.create(controller=controller)
        for order_dict in orders:
            controller = order_dict.pop("controller")
            strategy_modifications = order_dict.pop("StrategyModifications")
            connection_modifications = order_dict.pop("ConnectionModifications")
            architecture_modifications = order_dict.pop("ArchitectureModifications")

            order = Order.objects.create(batch=batches[controller], **order_dict)
            order_objects.append(order)
            for modification in strategy_modifications:
                StrategyModification.objects.create(order=order, **modification)
            for modification in connection_modifications:
                ConnectionModification.objects.create(order=order, **modification)
            for modification in architecture_modifications:
                ArchitectureModification.objects.create(order=order, **modification)

        for batch in batches.values():
            batch.set_status_ready()

        return order_objects, batches

    def get_orders__no_db(self, data: DataType, no_db_data: Optional[DBDataType] = None) -> list[dict]:
        """Get orders of the bot."""
        return self.architecture.get_orders__no_db(data=data, no_db_data=no_db_data)

    def connect_to_wallet(self, wallet: SpaceSimulationWallet | SpaceWallet) -> Connection:
        """Connect the bot to a (sim)space's wallet."""
        connection = Connection.objects.create(owner=wallet, bot=self)
        for plugin in self._strategy.plugins.all():
            plugin.connect(connection)
        self._strategy.connect(connection)
        return connection

    def copy(self) -> Bot:
        """Copy the instance bot."""
        return self.__class__.objects.create(
            name=f"Copy of {self.name}",
            strategy=self.strategy.copy(),
        )

    def value(self, space=None) -> float:  # noqa: ANN001
        """Return value market of the bot, depending of space containerization."""
        if space is None:
            return sum([connection.wallet.value() for connection in self.connections.all()])
        connection = Connection.objects.get(owner=space.wallet, bot=self)
        return connection.wallet.value()

    def get_stats(self, space=None) -> dict[str, str | int | float]:  # noqa: ANN001
        """Some bot's statistics used for KPI dashboards."""
        return {
            "value": self.value(space),
            "profit": 0,
            "delta_30": 0,  # TODO: Need history    # noqa
        }
