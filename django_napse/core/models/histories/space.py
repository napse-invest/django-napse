from django.db import models

from django_napse.core.models.histories.history import History


class SpaceHistory(History):
    owner = models.OneToOneField("Space", on_delete=models.CASCADE, related_name="history")
