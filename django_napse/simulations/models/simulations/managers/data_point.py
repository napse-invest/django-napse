from django.apps import apps
from django.db import models


class SimulationDataPointManager(models.Manager):
    def create(self, simulation, date, value: float, action: str, extra_info=None):
        SimulationDataPointExtraInfo = apps.get_model("django_napse_simulations", "SimulationDataPointExtraInfo")

        extra_info = extra_info or {}

        data_point = self.model(
            simulation=simulation,
            date=date,
            value=value,
            action=action,
        )
        data_point.save()
        for key, value in extra_info.items():
            SimulationDataPointExtraInfo.objects.create(
                data_point=data_point,
                key=key,
                value=value,
                target_type=type(value).__name__,
            )
        return data_point
