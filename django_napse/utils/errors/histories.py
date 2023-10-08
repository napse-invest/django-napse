class HistoryError(Exception):
    """Base class for History errors."""

    class InvalidDataPointFieldKey(Exception):
        """Raised when the key of a DataPointField is invalid."""
