class OrderError:
    """Base class for order errors."""

    class InvalidOrder(Exception):
        """Raised when a order is invalid."""

    class StatusError(Exception):
        """Raised when the status of an order is changed at the wrong time."""

    class ProcessError(Exception):
        """Raised when an error occurs during the processing of an order."""
