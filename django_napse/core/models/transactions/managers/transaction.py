from django.db import models

from django_napse.utils.constants import TRANSACTION_TYPES
from django_napse.utils.errors import TransactionError


class TransactionManager(models.Manager):
    def create(self, from_wallet, to_wallet, amount, ticker, transaction_type="TRANSFER"):
        """Create a Transaction object and update the wallets accordingly."""
        if amount == 0:
            return None
        transaction = self.model(
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=amount,
            ticker=ticker,
            transaction_type=transaction_type,
        )
        if from_wallet.space != to_wallet.space:
            error_msg = "Wallets must be on the same space."
            raise TransactionError.DifferentSpaceError(error_msg)
        if transaction_type not in TRANSACTION_TYPES:
            error_msg = f"Transaction type {transaction_type} not in {TRANSACTION_TYPES}."
            raise TransactionError.InvalidTransactionError(error_msg)

        from_wallet.spend(amount, ticker)
        to_wallet.top_up(amount, ticker, mbp=from_wallet.currencies.get(ticker=ticker).mbp)
        transaction.save()
        return transaction
