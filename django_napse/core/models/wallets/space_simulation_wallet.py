from typing import TYPE_CHECKING

from django.db import models

from django_napse.core.models.connections.connection import Connection
from django_napse.core.models.wallets.wallet import Wallet

if TYPE_CHECKING:
    from django_napse.core.models.accounts.exchange import ExchangeAccount
    from django_napse.core.models.accounts.space import Space
    from django_napse.core.models.bots.bot import Bot


class SpaceSimulationWallet(Wallet):
    """A Wallet owned by a Space for simulation purposes."""

    owner = models.OneToOneField("Space", on_delete=models.CASCADE, related_name="simulation_wallet")

    def __str__(self) -> str:  # pragma: no cover
        return f"WALLET: {self.pk=}. OWNER: {self.owner=}"

    @property
    def testing(self) -> bool:
        """Return whether the wallet is in testing mode."""
        return True

    @property
    def space(self) -> "Space":
        """Return the space that owns the wallet."""
        return self.owner

    @property
    def exchange_account(self) -> "ExchangeAccount":
        """Return the exchange account that contains the wallet."""
        return self.space.exchange_account.find()

    def reset(self) -> None:
        """Delete all currencies in the wallet."""
        self.currencies.all().delete()

    def connect_to_bot(self, bot: "Bot") -> "Connection":
        """Get or create connection to bot."""
        try:
            connection = self.connections.get(owner=self, bot=bot)
        except Connection.DoesNotExist:
            connection = Connection.objects.create(owner=self, bot=bot)
        return connection
