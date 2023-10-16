class SpaceError:
    """Base class for exchange account errors."""

    class DeleteError(Exception):
        """Raised when a space cannot be deleted."""
