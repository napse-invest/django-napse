from django.db import models

from django_napse.core.models.bots.config import BotConfig


class TurboDCABotConfig(BotConfig):
    setting_timeframe = models.DurationField()
    setting_percentage = models.FloatField()

    def __str__(self) -> str:
        return f"TURBO DCA BOT CONFIG: {self.pk} - {self.immutable}"
