from django.db import models

from django_napse.core.models.bots.strategy import Strategy
from django_napse.utils.constants import SIDES


class EmptyStrategy(Strategy):
    config = models.OneToOneField("EmptyBotConfig", on_delete=models.CASCADE, related_name="strategy")
    architecture = models.OneToOneField("SinglePairArchitecture", on_delete=models.CASCADE, related_name="strategy")

    def __str__(self) -> str:
        return f"EMPTY BOT STRATEGY: {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Strategy ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.config=}\n"
        string += f"{beacon}\t{self.architecture=}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string

    def give_order(self, data: dict) -> list[dict]:
        controller = data["controllers"]["main"]
        return [
            # {
            #     "controller": controller,
            #     "ArchitectureModifications": [],
            #     "StrategyModifications": [],
            #     "ConnectionModifications": [],
            #     "connection": data["connection"],
            #     "asked_for_amount": 0,
            #     "asked_for_ticker": controller.quote,
            #     "pair": controller.pair,
            #     "price": data["candles"][controller]["latest"]["close"],
            #     "side": SIDES.KEEP,
            # },
            # {
            #     "controller": controller,
            #     "ArchitectureModifications": [],
            #     "StrategyModifications": [],
            #     "ConnectionModifications": [],
            #     "connection": data["connection"],
            #     "asked_for_amount": 15 / data["candles"][controller]["latest"]["close"],
            #     "asked_for_ticker": controller.base,
            #     "pair": controller.pair,
            #     "price": data["candles"][controller]["latest"]["close"],
            #     "side": SIDES.SELL,
            # },
            {
                "controller": controller,
                "ArchitectureModifications": [],
                "StrategyModifications": [],
                "ConnectionModifications": [],
                "connection": data["connection"],
                "asked_for_amount": 15,
                "asked_for_ticker": controller.quote,
                "pair": controller.pair,
                "price": data["candles"][controller]["latest"]["close"],
                "side": SIDES.BUY,
            },
            {
                "controller": controller,
                "ArchitectureModifications": [],
                "StrategyModifications": [],
                "ConnectionModifications": [],
                "connection": data["connection"],
                "asked_for_amount": 20,
                "asked_for_ticker": controller.quote,
                "pair": controller.pair,
                "price": data["candles"][controller]["latest"]["close"],
                "side": SIDES.BUY,
            },
        ]
