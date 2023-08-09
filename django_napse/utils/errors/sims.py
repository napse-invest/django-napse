class SimError:
    """Base class for simulation errors."""

    class BotSimQueueError(Exception):
        """Raised when an error occurs in a BotSimQueue."""

    class CancelledSimulationError(Exception):
        """Raised when a simulation is cancelled."""


class DataSetError:
    """Base class for DataSet errors."""

    class DataSetQueueError(Exception):
        """Raised when an error occurs in a DataSetQueue."""

    class InvalidSettings(Exception):
        """Raised when an invalid setting is passed."""
