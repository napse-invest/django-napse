import uuid
from datetime import datetime, timedelta

from django.db import models
from django.utils.timezone import get_default_timezone

from django_napse.core.models.bots.bot import Bot
from django_napse.core.models.connections.connection import Connection
from django_napse.core.models.fleets.managers import FleetManager
from django_napse.core.models.orders.order import Order
from django_napse.utils.errors import BotError


class Fleet(models.Model):
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

    objects = FleetManager()

    def __str__(self):
        return f"FLEET: {self.pk=}, name={self.name}"

    def info(self, verbose=True, beacon=""):
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
    def testing(self):
        return self.exchange_account.testing

    @property
    def bots(self):
        return Bot.objects.filter(link__cluster__fleet=self)

    @property
    def value(self) -> float:
        """Sum value of all bots in fleet."""
        connections = Connection.objects.filter(bot__in=self.bots)
        return sum([connection.wallet.value_market() for connection in connections])

    def space_frame_value(self, space) -> float:
        """Sum value of all bots connected to the space."""
        # TODO: remove property to values and add the following lines to the new `value()` method
        fleet_connections = Connection.objects.filter(bot__in=self.bots)
        space_connections = space.wallet.connections.all()
        commun_connections = space_connections.intersection(fleet_connections)
        return sum([connection.wallet.value_market() for connection in commun_connections])

    def bot_clusters(self):
        bot_clusters = []
        for cluster in self.clusters.all():
            bot_clusters.append(Bot.objects.filter(link__cluster=cluster))
        return bot_clusters

    def connect_to_space(self, space):
        ...

    def invest(self, space, amount, ticker):
        connections = []
        for cluster in self.clusters.all():
            connections += cluster.invest(space, amount * cluster.share, ticker)
        return connections

    def bot_count(self, space=None) -> int:
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
            "delta_30": 0,  # TODO: Need history
        }

    def delete(self) -> None:
        """Delete clusters & relative (template) bots."""
        self.bots.delete()
        self.clusters.all().delete()
        super().delete()
