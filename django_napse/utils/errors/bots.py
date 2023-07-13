class BotError:
    """Base class for bot errors."""

    class InvalidSetting(Exception):
        """Raised when a bot is invalid."""


class BotConfigError:
    """Base class for bot config errors."""

    class MissingSettingError(Exception):
        """Raised when a setting is missing."""

    class DuplicateBotConfig(Exception):
        """Raised if an identical BotConfig already exists in this space."""


class ControllerError:
    """Base class for controller errors."""

    class InvalidSetting(Exception):
        """Raised when a controller is invalid."""

    class InvalidTicker(Exception):
        """Raised when a ticker is invalid."""

    class InvalidPair(Exception):
        """Raised when a pair is invalid."""


class ClusterError:
    """Base class for cluster errors."""

    class MutableBotConfig(Exception):
        """Raised when a BotConfig in a cluster is mutable."""

    class NotEmpty(Exception):
        """Raised when a cluster is not empty and you try to cr."""
