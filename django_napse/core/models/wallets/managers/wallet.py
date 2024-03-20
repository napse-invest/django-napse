from typing import TYPE_CHECKING

from django.apps import apps
from django.db import models

from django_napse.core.models.histories.wallet import WalletHistory
from django_napse.utils.errors import WalletError

if TYPE_CHECKING:
    from django_napse.core.models.wallets.wallet import Wallet


class WalletManager(models.Manager):
    """Manager for the Wallet model."""

    def create(self, title: str, owner: models.Model) -> "Wallet":
        """Create a Wallet object.

        Args:
            title (str): The title of the wallet.
            owner (models.Model): The owner of the wallet.

        Raises:
            WalletError.CreateError: If the model is a Wallet (you should use a subclass instead.)

        Returns:
            Wallet: The created wallet.
        """
        if self.model == apps.get_model("django_napse_core", "Wallet"):
            error_msg = "WalletManager cannot create a Wallet object. Use a subclass instead."
            raise WalletError.CreateError(error_msg)
        wallet = self.model(title=title, owner=owner)
        wallet.save()
        WalletHistory.get_or_create(owner=wallet)
        return wallet
