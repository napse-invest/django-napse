from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Union

from django.db import models

from django_napse.core.models.fleets.cluster import Cluster
from django_napse.utils.errors import FleetError

if TYPE_CHECKING:
    from django_napse.core.models.accounts.exchange import ExchangeAccount
    from django_napse.core.models.bots.bot import Bot
    from django_napse.core.models.fleets.fleet import Fleet


class FleetManager(models.Manager):
    """Manager for the Fleet model."""

    def create(
        self,
        name: str,
        exchange_account: ExchangeAccount,
        clusters: Optional[list[dict[Literal["template_bot", "share", "breakpoint", "autoscale"], Union[float, Bot]]]] = None,
    ) -> Fleet:
        """Create a new fleet."""
        clusters = clusters or []

        if sum(cluster["share"] for cluster in clusters) != 1:
            error_message = "The sum of all shares must be 1."
            raise FleetError.InvalidShares(error_message)

        if len(clusters) == 0:
            error_msg = "A fleet must have at least one cluster."
            raise FleetError.InvalidClusters(error_msg)

        fleet = self.model(
            name=name,
            exchange_account=exchange_account,
        )

        fleet.save()

        for cluster in clusters:
            cluster["template_bot"] = cluster["template_bot"].copy()
            Cluster.objects.create(fleet=fleet, **cluster)

        fleet.setup_finished = True
        fleet.save()
        return fleet
