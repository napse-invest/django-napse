from django.db import models

from django_napse.core.models.bots.config import BotConfig


class EmptyBotConfig(BotConfig):
    setting_empty = models.BooleanField()

    def __str__(self) -> str:
        return f"DCA BOT CONFIG: {self.pk} - {self.immutable}"
