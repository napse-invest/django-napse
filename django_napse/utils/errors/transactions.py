class TransactionError:
    """Base class for transaction errors."""

    class DifferentSpaceError(Exception):
        """Raised when the from and to wallets are on different spaces."""

    class InvalidTransactionError(Exception):
        """Raised when the transaction is invalid."""
