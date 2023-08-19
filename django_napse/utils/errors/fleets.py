class FleetError:
    """Base class for fleet errors."""

    class FleetNotSetupError(Exception):
        """Raised when a fleet is not setup, but you ask I to start trading or scaling."""

    class InvalidOperator(Exception):
        """Raised when the operator is invalid."""

    class InvalidShares(Exception):
        """Raised when the sum of all shares is not 1."""

    class InvalidClusters(Exception):
        """Raised when the fleet has no clusters."""
