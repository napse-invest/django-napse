class NapseKeyError:
    """Base class for NapseKey errors."""

    class DuplicateMasterkey(Exception):
        """When a masterkey is already in use."""
