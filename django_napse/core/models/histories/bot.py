from django.db import models

from django_napse.core.models.histories.history import History


class BotHistory(History):
    owner = models.OneToOneField("Bot", on_delete=models.CASCADE, related_name="history")
