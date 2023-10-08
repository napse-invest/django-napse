from django.db import models

from django_napse.core.models.histories.history import History


class FleetHistory(History):
    owner = models.OneToOneField("Fleet", on_delete=models.CASCADE, related_name="history")
