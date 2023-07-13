class WalletError:
    """Base class for wallet errors."""

    class SpendError(Exception):
        """Raised when a wallet cannot spend."""

    class TopUpError(Exception):
        """Raised when a wallet cannot top up."""

    class CreateError(Exception):
        """Raised when a wallet cannot be created."""
