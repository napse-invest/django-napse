class NapseError:
    """Base class for exceptions in this module."""

    class SettingsError(Exception):
        """Exception raised for errors in the settings file."""

    class RandomGenrationError(Exception):
        """Exception raised for errors in random generation processes."""
