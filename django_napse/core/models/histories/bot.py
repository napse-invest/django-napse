from django.db import models

from django_napse.core.models.histories.history import History


class BotHistory(History):
    """A History for a Bot.

    Use it to track the evolution of a bot over time.

    This tracks the following fields:
    TODO
    """

    owner = models.OneToOneField("Bot", on_delete=models.CASCADE, related_name="history")

    def generate_data_points(self) -> None:
        """Create a new data point for the bot."""
        return
