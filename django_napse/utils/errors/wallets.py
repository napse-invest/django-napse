class WalletError:
    """Base class for wallet errors."""

    class SpendError(Exception):
        """Raised when a wallet cannot spend."""

    class TopUpError(Exception):
        """Raised when a wallet cannot top up."""

    class CreateError(Exception):
        """Raised when a wallet cannot be created."""

    class UnavailableTicker(Exception):
        """Raised when a ticker is the wallet's currencies."""
