import uuid
from datetime import datetime, timedelta

from django.db import models
from django.utils.timezone import get_default_timezone

from django_napse.core.models.accounts.managers import NapseSpaceManager
from django_napse.core.models.fleets.fleet import Fleet
from django_napse.core.models.orders.order import Order
from django_napse.utils.errors import SpaceError


class NapseSpace(models.Model):
    name = models.CharField(max_length=200)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField()
    exchange_account = models.ForeignKey("ExchangeAccount", on_delete=models.CASCADE, related_name="spaces")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = NapseSpaceManager()

    class Meta:
        unique_together = ("name", "exchange_account")

    def __str__(self):
        return f"SPACE: {self.name}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Space ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.name=}\n"
        string += f"{beacon}\t{self.uuid=}\n"
        string += f"{beacon}Exchange Account:\n"
        new_beacon = beacon + "\t"
        string += f"{self.exchange_account.info(verbose=False, beacon=new_beacon)}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def testing(self):
        return self.exchange_account.testing

    @property
    def value(self) -> float:
        connections = self.wallet.connections.all()
        return sum([connection.wallet.value_market() for connection in connections])

    @property
    def fleets(self) -> models.QuerySet:
        connections = self.wallet.connections.all()
        return Fleet.objects.filter(clusters__links__bot__connections__in=connections).distinct()

    def get_stats(self) -> dict:
        order_count_30 = Order.objects.filter(
            connection__in=self.wallet.connections.all(),
            created_at__gt=datetime.now(tz=get_default_timezone()) - timedelta(days=30),
        ).count()

        return {
            "value": self.value,
            "order_count_30": order_count_30,
            "change_30": None,  # need history on space's value
        }

    def delete(self) -> None:
        if self.testing:
            return super().delete()
        if self.value > 0:
            raise SpaceError.DeleteError
        return super().delete()
