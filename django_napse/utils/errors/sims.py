class SimError:
    """Base class for simulation errors."""

    class DataSetQueueError(Exception):
        """Raised when an error occurs in a DataSetQueue."""

    class BotSimQueueError(Exception):
        """Raised when an error occurs in a BotSimQueue."""

    class CancelledSimulationError(Exception):
        """Raised when a simulation is cancelled."""
