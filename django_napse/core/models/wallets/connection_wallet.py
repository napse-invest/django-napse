from typing import TYPE_CHECKING

from django.db import models

from django_napse.core.models.wallets.wallet import Wallet

if TYPE_CHECKING:
    from django_napse.core.models.accounts.exchange import ExchangeAccount
    from django_napse.core.models.accounts.space import Space


class ConnectionWallet(Wallet):
    """A Wallet owned by a Connection."""

    owner = models.OneToOneField("Connection", on_delete=models.CASCADE, related_name="wallet")

    def __str__(self) -> str:  # pragma: no cover
        return f"WALLET: {self.pk=}. OWNER: {self.owner=}"

    @property
    def space(self) -> "Space":
        """Return the space that owns the wallet."""
        return self.owner.space

    @property
    def exchange_account(self) -> "ExchangeAccount":
        """Return the exchange account that contains the wallet."""
        return self.space.exchange_account.find()
