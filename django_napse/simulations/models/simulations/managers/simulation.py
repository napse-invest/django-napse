from django.apps import apps
from django.db import models

from django_napse.utils.errors import SimulationError


class SimulationManager(models.Manager):
    def create(self, space, bot, start_date, end_date, simulation_reference, data):
        SimulationDataPoint = apps.get_model("django_napse_simulations", "SimulationDataPoint")
        SimulationDataPointExtraInfo = apps.get_model("django_napse_simulations", "SimulationDataPointExtraInfo")

        simulation = self.model(
            space=space,
            bot=bot,
            start_date=start_date,
            end_date=end_date,
            simulation_reference=simulation_reference,
        )
        simulation.save()

        if data == {}:
            return simulation
        must_have = ["dates", "values", "actions", "amounts", "tickers"]
        for key in must_have:
            if key not in data:
                error_msg = f"Key {key} not in data"
                raise ValueError(error_msg)

        first_length = len(data["dates"])
        for key, value in data.items():
            if len(value) != first_length:
                error_msg = f"Key {key} has length {len(value)} but should have length {first_length}"
                raise SimulationError.InvalidData(error_msg)

        extra_info_keys = [key for key in data if key not in must_have]

        simulation.save()
        bulk_list_data_point = []
        bulk_list_extra_info = []
        for info in zip(
            data["dates"],
            data["values"],
            data["actions"],
            data["amounts"],
            data["tickers"],
            *[data[key] for key in extra_info_keys],
            strict=True,
        ):
            date = info[0]
            value = info[1]
            action = info[2]
            amount = info[3]
            ticker = info[4]
            extra_info = {key: info[i + 5] for i, key in enumerate(extra_info_keys)}
            bulk_list_data_point.append(
                SimulationDataPoint(
                    simulation=simulation,
                    date=date,
                    value=value,
                    action=action,
                    amount=amount,
                    ticker=ticker,
                ),
            )
            for key, value in extra_info.items():
                bulk_list_extra_info.append(
                    SimulationDataPointExtraInfo(
                        data_point=bulk_list_data_point[-1],
                        key=key,
                        value=str(value),
                        target_type=type(value).__name__,
                    ),
                )

            if len(bulk_list_data_point) == 1000 or date == data["dates"][-1]:
                SimulationDataPoint.objects.bulk_create(bulk_list_data_point)
                bulk_list_data_point = []
                SimulationDataPointExtraInfo.objects.bulk_create(bulk_list_extra_info)
                bulk_list_extra_info = []

        return simulation
