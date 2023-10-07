from django.db import models

from django_napse.core.models.histories.history import History


class WalletHistory(History):
    owner = models.OneToOneField("Wallet", on_delete=models.CASCADE, related_name="history")
