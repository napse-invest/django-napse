import uuid

from django.db import models

from django_napse.core.models import BotConfig, NapseSpace
from django_napse.simulations.models.sims.managers import BotSimManager


# Create your models here.
class BotSim(models.Model):
    simulation_reference = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, null=True)
    space = models.ForeignKey(NapseSpace, on_delete=models.CASCADE, null=True)
    bot_type = models.CharField(max_length=255, default="Bot")
    investment = models.FloatField(default=1000)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BotSimManager()

    def __str__(self) -> str:  # pragma: no cover$
        return f"BOT SIM {self.pk}"


class BotSimSetting(models.Model):
    bot_sim = models.ForeignKey(BotSim, on_delete=models.CASCADE, related_name="settings")
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100)

    def __str__(self) -> str:  # pragma: no cover
        return f"BOT SIM SETTING {self.pk}"


class BotSimDataPoint(models.Model):
    bot_sim = models.ForeignKey(BotSim, on_delete=models.CASCADE, related_name="data_points")
    date = models.DateTimeField()
    price = models.FloatField()
    value = models.FloatField()
    base = models.FloatField()
    quote = models.FloatField()
    mbp = models.FloatField(null=True)
    amount = models.FloatField(null=True)
    action = models.CharField(max_length=4)

    def __str__(self):  # pragma: no cover
        return f"BOT SIM DATA POINT {self.pk}"


class BotSimQueue(models.Model):
    simulation_reference = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    bot_config = models.ForeignKey(BotConfig, on_delete=models.CASCADE)
    investment = models.FloatField(default=1000)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    canceled = models.BooleanField(default=False)

    status = models.CharField(max_length=12, default="IDLE")
    completion = models.FloatField(default=0.0)
    eta = models.DurationField(blank=True, null=True)

    error = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"BOT SIM QUEUE {self.pk}"
