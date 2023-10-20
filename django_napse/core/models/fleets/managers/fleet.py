from django.db import models

from django_napse.core.models.fleets.cluster import Cluster
from django_napse.utils.errors import FleetError


class FleetManager(models.Manager):
    def create(
        self,
        name,
        exchange_account,
        clusters=None,
    ):
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
