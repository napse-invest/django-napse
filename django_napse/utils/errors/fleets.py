class FleetError:
    """Base class for fleet errors."""

    class FleetNotSetupError(Exception):
        """Raised when a fleet is not setup, but you ask I to start trading or scaling."""

    class InvalidOperator(Exception):
        """Raised when the operator is invalid."""
