from django.db import models

from django_napse.core.models.histories.history import History


class ExchangeAccountHistory(History):
    owner = models.OneToOneField("ExchangeAccount", on_delete=models.CASCADE, related_name="history")
