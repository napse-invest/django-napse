from django.db import models

from django_napse.core.models.bots.config import BotConfig


class DCABotConfig(BotConfig):
    setting_timeframe = models.DurationField()

    def __str__(self) -> str:
        return f"DCA BOT CONFIG: {self.pk} - {self.immutable}"
