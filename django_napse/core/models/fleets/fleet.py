import uuid

from django.db import models

from django_napse.core.models.bots.bot import Bot
from django_napse.core.models.fleets.managers import FleetManager


class Fleet(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, default="Fleet")
    exchange_account = models.ForeignKey("ExchangeAccount", on_delete=models.CASCADE)
    running = models.BooleanField(default=False)
    setup_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    objects = FleetManager()

    def __str__(self):
        return f"FLEET: {self.pk=}, name={self.name}"

    @property
    def testing(self):
        return self.exchange_account.testing

    @property
    def bots(self):
        return Bot.objects.filter(link__cluster__fleet=self)

    def bot_clusters(self):
        bot_clusters = []
        for cluster in self.cluster:
            bot_clusters.append(Bot.objects.filter(link__cluster=cluster))
        return bot_clusters


class DefaultFleetOperator(models.Model):
    fleet = models.OneToOneField("Fleet", on_delete=models.CASCADE, related_name="operator")

    def __str__(self) -> str:
        return f"DEFAULT_FLEET_OPERATOR: {self.pk=}, fleet__name={self.fleet.name}"


class EquilibriumFleetOperator(DefaultFleetOperator):
    pass


class SpecificSharesFleetOperator(DefaultFleetOperator):
    pass


class SpecificShare(models.Model):
    cluster = models.OneToOneField("Cluster", on_delete=models.CASCADE, related_name="specific_shares")
    operator = models.ForeignKey(DefaultFleetOperator, on_delete=models.CASCADE, related_name="specific_shares")
    share = models.FloatField()

    class Meta:
        unique_together = ("cluster", "operator")

    def __str__(self) -> str:
        return f"SPECIFIC_SHARE: {self.pk=}, operator={self.operator}, share={self.share}"


class SpecificBreakPoint(models.Model):
    cluster = models.OneToOneField("Cluster", on_delete=models.CASCADE, related_name="specific_breakpoints")
    operator = models.ForeignKey(DefaultFleetOperator, on_delete=models.CASCADE, related_name="specific_breakpoints")
    scale_up_breakpoint = models.FloatField()

    class Meta:
        unique_together = ("cluster", "operator")

    def __str__(self) -> str:
        return f"SPECIFIC_BREAKPOINT: {self.pk=}, operator={self.operator}, scale_up_breakpoint={self.scale_up_breakpoint}"


class SpecificAutoscale(models.Model):
    cluster = models.OneToOneField("Cluster", on_delete=models.CASCADE, related_name="specific_autoscales")
    operator = models.ForeignKey(DefaultFleetOperator, on_delete=models.CASCADE, related_name="specific_autoscales")
    autoscale = models.BooleanField(default=True)

    class Meta:
        unique_together = ("cluster", "operator")

    def __str__(self) -> str:
        return f"SPECIFIC_AUTOSCALE: {self.pk=}, operator={self.operator}, autoscale={self.autoscale}"
