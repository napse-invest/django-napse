import uuid

from django.db import models

from django_napse.core.models import Credit
from django_napse.simulations.models import DataSet
from django_napse.simulations.models.simulations.managers import SimulationDataPointManager, SimulationManager, SimulationQueueManager
from django_napse.utils.constants import SIMULATION_STATUS
from django_napse.utils.usefull_functions import process_value_from_type


class Simulation(models.Model):
    simulation_reference = models.UUIDField(unique=True, editable=False, null=True)
    space = models.ForeignKey("django_napse_core.NapseSpace", on_delete=models.CASCADE, null=True)
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

    objects = SimulationDataPointManager()

    def __str__(self):
        return f"SIMULATION DATA POINT {self.pk}"

    def to_dict(self):
        extra_info = self.extra_info.all()
        return {
            "date": self.date,
            "value": self.value,
            "action": self.action,
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


class SimulationQueue(models.Model):
    simulation_reference = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    space = models.ForeignKey("django_napse_core.NapseSpace", on_delete=models.CASCADE, null=True)
    bot = models.OneToOneField("django_napse_core.Bot", on_delete=models.CASCADE, null=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    canceled = models.BooleanField(default=False)

    status = models.CharField(max_length=12, default=SIMULATION_STATUS.IDLE)
    completion = models.FloatField(default=0.0)
    eta = models.DurationField(blank=True, null=True)

    error = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = SimulationQueueManager()

    def __str__(self) -> str:
        return f"BOT SIM QUEUE {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}SimulationQueue {self.pk}:\n"
        string += f"{beacon}\t{self.bot=}\n"
        string += f"{beacon}\t{self.space=}\n"

        string += f"{beacon}\t{self.start_date=}\n"
        string += f"{beacon}\t{self.end_date=}\n"
        string += f"{beacon}\t{self.created_at=}\n"

        string += f"{beacon}Investments:\n"
        investments = self.investments.all()
        if investments.count() > 0:
            for investment in investments:
                string += f"{beacon}\t{investment}\n"
        else:
            string += f"{beacon}\tNo investments\n"
        if verbose:
            print(string)
        return string

    def setup_simulation(self):
        print(self.space.simulation_wallet)
        self.space.simulation_wallet.find().reset()
        for investment in self.investments.all():
            Credit.objects.create(
                wallet=self.space.simulation_wallet,
                ticker=investment.ticker,
                amount=investment.amount,
            )
        new_bot = self.bot.copy()
        connection = new_bot.connect_to(self.space.simulation_wallet)
        for investment in self.investments.all():
            connection.deposit(investment.ticker, investment.amount)
        return new_bot

    def cleanup_simulation(self, bot):
        self.space.simulation_wallet.reset()
        bot.hibernate()

    def quick_simulation(self, bot):
        dataset = DataSet.objects.create(controller=bot.controller, start_date=self.start_date, end_date=self.end_date)
        dataframe = dataset.to_dataframe(start_date=self.start_date, end_date=self.end_date)
        for index, row in dataframe.iterrows():
            print(index, row)

    def run_quicksim(self):
        self.status = SIMULATION_STATUS.RUNNING
        self.save()
        bot = self.setup_simulation()

        simulation = self.quicksim(bot=self.bot)

        self.cleanup_simulation(bot)
        self.status = SIMULATION_STATUS.IDLE
        self.save()
        return simulation

    def is_finished(self):
        return self.status == SIMULATION_STATUS.IDLE and self.completion == 100

    def get_status(self):
        """Return a dictionary with the status of the BotSimQueue.

        Dict shape:
        ```json
        {
            "status": "RUNNING",
            "completion": 56.9,
            "eta": 00:01:04,
            "position_in_queue": 0,
            "error": false,
        }
        ```
        """
        return {
            "status": self.status,
            "completion": self.completion,
            "eta": self.eta,
            "position_in_queue": SimulationQueue.objects.filter(created_at__lt=self.created_at, error=False).count(),
            "error": self.error,
        }

    def cancel(self):
        """Stop the BotSim."""
        self.canceled = True
        self.save()
