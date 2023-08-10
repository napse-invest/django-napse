from django.db import models


class SimulationInvestedCurrency(models.Model):
    owner = models.ForeignKey("Simulation", on_delete=models.CASCADE, related_name="investments")
    ticker = models.CharField(max_length=10)
    amount = models.FloatField(default=0)

    class Meta:
        unique_together = ("owner", "ticker")

    def __str__(self):
        return f"SIMULATION INVESTED CURRENCY {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Currency ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.owner=}\n"
        string += f"{beacon}\t{self.mbp=}\n"
        string += f"{beacon}\t{self.ticker=}\n"
        string += f"{beacon}\t{self.amount=}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def testing(self):
        return self.wallet.testing


class SimulationQueueInvestedCurrency(models.Model):
    owner = models.ForeignKey("SimulationQueue", on_delete=models.CASCADE, related_name="investments")
    ticker = models.CharField(max_length=10)
    amount = models.FloatField(default=0)

    class Meta:
        unique_together = ("owner", "ticker")

    def __str__(self):
        return f"SIMULATION QUEUE INVESTED CURRENCY {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Currency ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.owner=}\n"
        string += f"{beacon}\t{self.mbp=}\n"
        string += f"{beacon}\t{self.ticker=}\n"
        string += f"{beacon}\t{self.amount=}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def testing(self):
        return self.wallet.testing
