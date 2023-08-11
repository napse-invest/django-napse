from django.db import models
from django.db.transaction import atomic

from django_napse.utils.constants import TRANSACTION_TYPES
from django_napse.utils.errors import TransactionError


class TransactionManager(models.Manager):
    @atomic()
    def create(self, from_wallet, to_wallet, amount, ticker, transaction_type):
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
        if from_wallet.exchange_account != to_wallet.exchange_account:
            error_msg = "Wallets must be on the same exchange_account."
            raise TransactionError.DifferentAccountError(error_msg)

        if from_wallet == to_wallet:
            error_msg = "Wallets must be different."
            raise TransactionError.SameWalletError(error_msg)

        if from_wallet.testing != to_wallet.testing:
            error_msg = f"Wallets must be both testing or both not testing. Here: {from_wallet.testing} -> {to_wallet.testing}."
            raise TransactionError.TestingError(error_msg)

        if transaction_type not in TRANSACTION_TYPES:
            error_msg = f"Transaction type {transaction_type} not in {TRANSACTION_TYPES}."
            raise TransactionError.InvalidTransactionError(error_msg)

        from_wallet.spend(amount, ticker, force=True)
        to_wallet.top_up(amount, ticker, mbp=from_wallet.currencies.get(ticker=ticker).mbp, force=True)
        transaction.save()
        return transaction
