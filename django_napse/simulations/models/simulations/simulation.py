from django.db import models

from django_napse.simulations.models.simulations.managers import SimulationDataPointManager, SimulationManager
from django_napse.utils.usefull_functions import process_value_from_type


class Simulation(models.Model):
    simulation_reference = models.UUIDField(unique=True, editable=False, null=True)
    space = models.ForeignKey("django_napse_core.Space", on_delete=models.CASCADE, null=True)
    bot = models.OneToOneField("django_napse_core.Bot", on_delete=models.CASCADE, null=True, related_name="simulation")

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SimulationManager()

    def __str__(self) -> str:
        return f"SIMULATION {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Simulation {self.pk}:\n"
        string += f"{beacon}\t{self.bot=}\n"
        string += f"{beacon}\t{self.space=}\n"

        string += f"{beacon}\t{self.start_date=}\n"
        string += f"{beacon}\t{self.end_date=}\n"
        string += f"{beacon}\t{self.created_at=}\n"

        string += f"{beacon}Data points:\n"
        data_points = self.data_points.all().order_by("date")

        if data_points.count() > 10:
            for data_point in data_points[:5]:
                string += f"{beacon}\t{data_point.to_str()}\n"
            string += f"{beacon}\t...\n"
            for data_point in data_points[data_points.count() - 5 :]:
                string += f"{beacon}\t{data_point.to_str()}\n"
            string += f"{beacon}\t({data_points.count()} data points)\n"

        elif data_points.count() > 0:
            for data_point in data_points:
                string += f"{beacon}\t{data_point.to_str()}\n"

        else:
            string += f"{beacon}\tNo data points\n"
        if verbose:
            print(string)
        return string


class SimulationDataPoint(models.Model):
    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE, related_name="data_points")
    date = models.DateTimeField()
    value = models.FloatField()
    action = models.CharField(max_length=10)
    amount = models.FloatField()
    ticker = models.CharField(max_length=10)

    objects = SimulationDataPointManager()

    def __str__(self):
        return f"SIMULATION DATA POINT {self.pk}"

    def to_dict(self):
        extra_info = self.extra_info.all()
        return {
            "date": self.date,
            "value": self.value,
            "action": self.action,
            "amount": self.amount,
            "ticker": self.ticker,
            **{info.key: info.get_value() for info in extra_info},
        }

    def to_str(self):
        string = ""
        for key, value in self.to_dict().items():
            string += f"{key}: {value}\t"
        return string


class SimulationDataPointExtraInfo(models.Model):
    data_point = models.ForeignKey("SimulationDataPoint", on_delete=models.CASCADE, related_name="extra_info")
    key = models.CharField(max_length=64)
    value = models.CharField(max_length=64)
    target_type = models.CharField(max_length=64)

    def __str__(self):
        return f"SIMULATION DATA POINT EXTRA INFO {self.pk}"

    def get_value(self):
        return process_value_from_type(value=self.value, target_type=self.target_type)
