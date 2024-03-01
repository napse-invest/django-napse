from typing import TYPE_CHECKING

from django.db import models
from django.db.transaction import atomic

from django_napse.core.models.histories.wallet import WalletHistory

if TYPE_CHECKING:
    from django_napse.core.models.transactions.debit import Debit
    from django_napse.core.models.wallets.wallet import Wallet


class DebitManager(models.Manager):
    """Manager for the Debit model."""

    @atomic()
    def create(self, wallet: "Wallet", amount: float, ticker: str) -> "Debit":
        """Create a Debit object.

        Args:
            wallet (Wallet): The wallet to debit.
            amount (float): The amount to debit.
            ticker (str): The ticker of the currency to debit.

        Returns:
            Debit: The created debit.
        """
        if amount == 0:
            return None
        debit = self.model(
            wallet=wallet,
            amount=amount,
            ticker=ticker,
        )

        debit.save()
        wallet.spend(amount, ticker, force=True)
        WalletHistory.get_or_create(wallet).generate_data_point()
        return debit
