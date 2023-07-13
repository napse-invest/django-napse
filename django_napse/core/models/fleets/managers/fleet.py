from django.apps import apps
from django.db import models

from django_napse.core.models.fleets.cluster import Cluster
from django_napse.utils.constants import EXCHANGES, OPERATORS
from django_napse.utils.errors import FleetError


class FleetManager(models.Manager):
    def create(
        self,
        name,
        exchange_account,
        operator: str = "EQUILIBRIUM",
        operator_args=None,
        configs=None,
    ):
        """Create a fleet.

        Args:
        ----
        name (str): The name of the fleet
        exchange_account(str): The exchange account of the fleet
        operator (str): The operator of the fleet (default: "EQUILIBRIUM")
        operator_args (dict): The arguments to pass down to the operator (default: {})
        configs (list): The list of configs to use (default: None)

        Raises:
        ------
        ValueError: If the exchange or operator are invalid

        Returns:
        -------
        Fleet: The created fleet
        """
        operator_args = operator_args or {}
        configs = configs or []

        fleet = self.model(
            name=name,
            exchange_account=exchange_account,
        )

        if operator not in OPERATORS:
            error_message = f"Invalid operator: {operator}."
            raise FleetError.InvalidOperator(error_message)

        fleet.save()

        match operator:
            case "EQUILIBRIUM":
                EquilibriumFleetOperator = apps.get_model("django_napse_core", "EquilibriumFleetOperator")
                EquilibriumFleetOperator.objects.create(fleet=fleet, **operator_args)
            case "SPECIFIC_SHARES":
                SpecificSharesFleetOperator = apps.get_model("django_napse_core", "SpecificSharesFleetOperator")
                SpecificSharesFleetOperator.objects.create(fleet=fleet, **operator_args)

        for config in configs:
            cluster = Cluster.objects.create(fleet=fleet, config=config.duplicate_immutable())
            cluster.deploy()

        return fleet
