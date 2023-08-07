from django.db import models

from django_napse.core.models.bots.strategy import Strategy


class EmptyStrategy(Strategy):
    config = models.OneToOneField("EmptyBotConfig", on_delete=models.CASCADE, related_name="strategy")
    architechture = models.OneToOneField("SinglePairArchitechture", on_delete=models.CASCADE, related_name="strategy")

    def __str__(self) -> str:
        return f"EMPTY BOT STRATEGY: {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Strategy ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.config=}\n"
        string += f"{beacon}\t{self.architechture=}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string
