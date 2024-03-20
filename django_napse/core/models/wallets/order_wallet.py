from typing import TYPE_CHECKING

from django.db import models

from django_napse.core.models.wallets.wallet import Wallet

if TYPE_CHECKING:
    from django_napse.core.models.accounts.exchange import ExchangeAccount


class OrderWallet(Wallet):
    """A Wallet owned by an Order."""

    owner = models.OneToOneField("Order", on_delete=models.CASCADE, related_name="wallet")

    def __str__(self) -> str:  # pragma: no cover
        return f"WALLET: {self.pk=}. OWNER: {self.owner=}"

    @property
    def exchange_account(self) -> "ExchangeAccount":
        """Return the exchange account that contains the wallet."""
        return self.owner.exchange_account.find()
