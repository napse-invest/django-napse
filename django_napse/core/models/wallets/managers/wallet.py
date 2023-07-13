from django.apps import apps
from django.db import models

from django_napse.utils.errors import WalletError


class WalletManager(models.Manager):
    def create(self, title: str, owner):
        """Create the wallet."""
        if self.model == apps.get_model("django_napse_core", "Wallet"):
            error_msg = "WalletManager cannot create a Wallet object. Use a subclass instead."
            raise WalletError.CreateError(error_msg)

        return super().create(
            title=title,
            owner=owner,
        )
