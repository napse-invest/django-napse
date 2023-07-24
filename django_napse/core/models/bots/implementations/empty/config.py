from django_napse.core.models.bots.config import BotConfig


class EmptyBotConfig(BotConfig):
    bot_type = "Empty"

    def __str__(self) -> str:
        return f"EMPTY BOT CONFIG: {self.pk} - {self.immutable}"
