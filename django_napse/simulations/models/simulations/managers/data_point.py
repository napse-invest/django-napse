from django.apps import apps
from django.db import models


class SimulationDataPointManager(models.Manager):
    def create(self, simulation, date, value: float, action: str, amount: float, ticker: str, extra_info=None):
        SimulationDataPointExtraInfo = apps.get_model("django_napse_simulations", "SimulationDataPointExtraInfo")

        extra_info = extra_info or {}

        data_point = self.model(
            simulation=simulation,
            date=date,
            value=value,
            action=action,
            amount=amount,
            ticker=ticker,
        )
        data_point.save()
        for key, value in extra_info.items():
            print(key, value)
            SimulationDataPointExtraInfo.objects.create(
                data_point=data_point,
                key=key,
                value=str(value),
                target_type=type(value).__name__,
            )
        return data_point
