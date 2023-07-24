from django.db import models

from django_napse.core.models.bots.strategy import Strategy


class EmptyStrategy(Strategy):
    config = models.ForeignKey("EmptyBotConfig", on_delete=models.CASCADE, related_name="empty_bot_strategies")

    def __str__(self) -> str:
        return f"EMPTY BOT STRATEGY: {self.pk}"
