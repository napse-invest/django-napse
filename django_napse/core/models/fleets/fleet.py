from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from django.db import models
from django.utils.timezone import get_default_timezone

from django_napse.core.models.bots.bot import Bot
from django_napse.core.models.connections.connection import Connection
from django_napse.core.models.fleets.managers import FleetManager
from django_napse.core.models.orders.order import Order
from django_napse.utils.errors import BotError

if TYPE_CHECKING:
    from django_napse.core.models.accounts.space import Space


class Fleet(models.Model):
    """A fleet manages bots & scale them horizontally through manager."""

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    name = models.CharField(
        max_length=100,
        default="Fleet",
    )
    exchange_account = models.ForeignKey(
        "ExchangeAccount",
        on_delete=models.CASCADE,
    )
    running = models.BooleanField(default=False)
    setup_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
    )

    objects: FleetManager = FleetManager()

    def __str__(self) -> str:
        return f"FLEET: {self.pk=}, name={self.name}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}Fleet {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.name=}\n"
        string += f"{beacon}\t{self.exchange_account=}\n"
        string += f"{beacon}\t{self.running=}\n"
        string += f"{beacon}\t{self.setup_finished=}\n"

        string += f"{beacon}Clusters:\n"
        new_beacon = beacon + "\t"
        for cluster in self.clusters.all():
            string += f"{beacon}{cluster.info(verbose=False, beacon=new_beacon)}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def testing(self) -> bool:
        """Return testing status of the relative exchange account."""
        return self.exchange_account.testing

    @property
    def bots(self) -> models.QuerySet[Bot]:
        """Return QuerySet of all fleet's bots."""
        return Bot.objects.filter(link__cluster__fleet=self)

    @property
    def value(self) -> float:
        """Sum value of all bots in fleet."""
        connections = Connection.objects.filter(bot__in=self.bots)
        return sum([connection.wallet.value() for connection in connections])

    def space_frame_value(self, space: Space) -> float:
        """Sum value of all bots connected to the space."""
        # TODO: remove property to values and add the following lines to the new `value()` method # noqa
        fleet_connections = Connection.objects.filter(bot__in=self.bots)
        space_connections = space.wallet.connections.all()
        commun_connections = space_connections.intersection(fleet_connections)
        return sum([connection.wallet.value() for connection in commun_connections])

    def bot_clusters(self) -> list[Bot]:
        """Return list of bot containerized into clusters."""
        return [Bot.objects.filter(link__cluster=cluster) for cluster in self.clusters.all()]

    def connect_to_space(self, space: Space):  # noqa
        ...

    def invest(self, space: Space, amount: float, ticker: str) -> list[Connection]:
        """Invest from space to fleet."""
        connections = []
        for cluster in self.clusters.all():
            connections += cluster.invest(space, amount * cluster.share, ticker)
        return connections

    def bot_count(self, space: Space | None = None) -> int:
        """Count number of bots in fleet, depends on space frame."""
        query_bot = self.bots.all()
        if space is None:
            return len(query_bot)
        result = []
        for bot in query_bot:
            try:
                bot_space = bot.space
            except BotError.NoSpace:
                continue
            if bot_space == self.space:
                result.append(bot)
        return len(result)

    def get_stats(self) -> dict[str, str | int | float]:
        """Return Fleet's stats."""
        order_count = Order.objects.filter(  # noqa: F841
            connection__bot__in=self.bots,
            created_at__gt=datetime.now(tz=get_default_timezone()) - timedelta(days=30),
        ).count()
        return {
            "value": self.value,
            "bot_count": self.bot_count(),
            "delta_30": 0,  # TODO: Need history # noqa
        }

    def delete(self) -> None:
        """Delete clusters & relative (template) bots."""
        self.bots.delete()
        self.clusters.all().delete()
        super().delete()
