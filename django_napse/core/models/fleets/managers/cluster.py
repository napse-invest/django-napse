from django.apps import apps
from django.db import models


class ClusterManager(models.Manager):
    def create(self, fleet, share, breakpoint, autoscale):  # noqa A002
        SpecificShare = apps.get_model("django_napse_core", "SpecificShare")
        SpecificBreakPoint = apps.get_model("django_napse_core", "SpecificBreakPoint")
        SpecificAutoscale = apps.get_model("django_napse_core", "SpecificAutoscale")

        cluster = self.model(fleet=fleet)
        cluster.save()
        SpecificShare.objects.create(cluster=cluster, share=share)
        SpecificBreakPoint.objects.create(cluster=cluster, breakpoint=breakpoint)
        SpecificAutoscale.objects.create(cluster=cluster, autoscale=autoscale)
