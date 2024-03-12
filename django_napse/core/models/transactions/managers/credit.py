from typing import TYPE_CHECKING

from django.db import models
from django.db.transaction import atomic

from django_napse.core.models.histories.wallet import WalletHistory

if TYPE_CHECKING:
    from django_napse.core.models.transactions.credit import Credit
    from django_napse.core.models.wallets.wallet import Wallet


class CreditManager(models.Manager):
    """Manager for the Credit model."""

    @atomic()
    def create(self, wallet: "Wallet", amount: float, ticker: str) -> "Credit":
        """Create a Credit object.

        Args:
            wallet (Wallet): The wallet to credit.
            amount (float): The amount to credit.
            ticker (str): The ticker of the currency to credit.

        Returns:
            Credit: The created credit.
        """
        if amount == 0:
            return None
        credit = self.model(
            wallet=wallet,
            amount=amount,
            ticker=ticker,
        )

        credit.save()
        wallet.top_up(amount, ticker, force=True)
        WalletHistory.get_or_create(wallet).generate_data_point()
        return credit
