class ExchangeError:
    """Base class for exchange errors."""


class ExchangeAccountError:
    """Base class for exchange account errors."""

    class CreateError(Exception):
        """Raised when a exchange account cannot be created."""

    class APIPermissionError(Exception):
        """Raised when a exchange account cannot interact with the exchange API."""
