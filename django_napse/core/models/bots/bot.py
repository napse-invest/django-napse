import uuid
from typing import Optional

from django.db import models

from django_napse.core.models.connections.connection import Connection
from django_napse.core.models.modifications import ArchitectureModification, ConnectionModification, StrategyModification
from django_napse.core.models.orders.order import Order, OrderBatch
from django_napse.utils.errors import BotError


class Bot(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    name = models.CharField(max_length=100, default="Bot")

    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    strategy = models.OneToOneField("Strategy", on_delete=models.CASCADE, related_name="bot")

    def __str__(self):
        return f"BOT {self.pk=}"

    def save(self, *args, **kwargs):
        if self.is_in_simulation and self.is_in_fleet:
            error_msg = "Bot is in simulation and fleet."
            raise BotError.InvalidSetting(error_msg)
        return super().save(*args, **kwargs)

    def info(self, verbose=True, beacon=""):
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
    def is_in_simulation(self):
        return hasattr(self, "simulation")

    @property
    def is_in_fleet(self):
        return hasattr(self, "bot_in_cluster")

    @property
    def testing(self):
        if self.is_in_simulation:
            return True
        if self.is_in_fleet:
            return self.bot_in_cluster.cluster.fleet.testing
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    @property
    def space(self):
        if self.is_in_simulation:
            return self.simulation.space
        if self.is_in_fleet:
            error_msg = "Bot is in a fleet and therefore doesn't have a space."
            raise BotError.NoSpace(error_msg)
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    @property
    def exchange_account(self):
        if self.is_in_simulation:
            return self.simulation.space.exchange_account
        if self.is_in_fleet:
            return self.bot_in_cluster.cluster.fleet.exchange_account
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    @property
    def _strategy(self):
        return self.strategy.find()

    @property
    def architecture(self):
        return self._strategy.architecture.find()

    @property
    def controllers(self):
        return self.architecture.controllers_dict()

    def hibernate(self):
        if not self.active:
            error_msg = "Bot is already hibernating."
            raise BotError.InvalidSetting(error_msg)
        self.active = False
        self.save()

    def get_connections(self):
        return list(self.connections.all())

    def get_connection_data(self):
        return {connection: connection.to_dict() for connection in self.get_connections()}

    def get_orders(self, data: Optional[dict] = None, no_db_data: Optional[dict] = None):
        if not self.active:
            error_msg = "Bot is hibernating."
            raise BotError.InvalidSetting(error_msg)

        orders = self._get_orders(data=data, no_db_data=no_db_data)
        batches = {}
        order_objects = []
        for order in orders:
            controller = order["controller"]
            batches[controller] = OrderBatch.objects.create(controller=controller)
        for order in orders:
            controller = order.pop("controller")
            strategy_modifications = order.pop("StrategyModifications")
            connection_modifications = order.pop("ConnectionModifications")
            architecture_modifications = order.pop("ArchitectureModifications")
            order = Order.objects.create(batch=batches[controller], **order)
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

    def _get_orders(self, data: Optional[dict] = None, no_db_data: Optional[dict] = None):
        return self.architecture._get_orders(data=data, no_db_data=no_db_data)

    def connect_to(self, wallet):
        connection = Connection.objects.create(owner=wallet, bot=self)
        for plugin in self._strategy.plugins.all():
            plugin.connect(connection)
        self._strategy.connect(connection)
        return connection

    def copy(self):
        return self.__class__.objects.create(
            name=f"Copy of {self.name}",
            strategy=self.strategy.copy(),
        )
