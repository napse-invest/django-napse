from typing import TYPE_CHECKING

from django.db import models
from django.db.transaction import atomic

from django_napse.core.models.histories.wallet import WalletHistory
from django_napse.utils.constants import TRANSACTION_TYPES
from django_napse.utils.errors import TransactionError

if TYPE_CHECKING:
    from django_napse.core.models.transactions.transaction import Transaction
    from django_napse.core.models.wallets.wallet import Wallet


class TransactionManager(models.Manager):
    """The manager for the Transaction model."""

    @atomic()
    def create(self, from_wallet: "Wallet", to_wallet: "Wallet", amount: float, ticker: str, transaction_type: str) -> "Transaction":
        """Create a Transaction object and update the wallets accordingly.

        Args:
            from_wallet (Wallet): The wallet to take the money from.
            to_wallet (Wallet): The wallet to send the money to.
            amount (float): The amount of money to transfer.
            ticker (str): The ticker of the currency to transfer.
            transaction_type (str): The type of transaction.

        Raises:
            TransactionError.DifferentAccountError: If the wallets are on different exchange_accounts.
            TransactionError.SameWalletError: If the wallets are the same.
            TransactionError.TestingError: If the wallets are not both testing or both not testing.
            TransactionError.InvalidTransactionError: If the transaction type is not in TRANSACTION_TYPES.

        Returns:
            Transaction: The created transaction.
        """
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
        WalletHistory.get_or_create(from_wallet).generate_data_point()
        WalletHistory.get_or_create(to_wallet).generate_data_point()
        return transaction
