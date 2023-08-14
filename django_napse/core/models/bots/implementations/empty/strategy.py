from django_napse.core.models.bots.architectures.single_pair import SinglePairArchitecture
from django_napse.core.models.bots.implementations.empty.config import EmptyBotConfig
from django_napse.core.models.bots.strategy import Strategy
from django_napse.utils.constants import SIDES


class EmptyStrategy(Strategy):
    def __str__(self) -> str:
        return f"EMPTY BOT STRATEGY: {self.pk=}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Strategy ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.config=}\n"
        string += f"{beacon}\t{self.architecture=}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string

    @classmethod
    def config_class(cls):
        return EmptyBotConfig

    @classmethod
    def architecture_class(cls):
        return SinglePairArchitecture

    def give_order(self, data: dict) -> list[dict]:
        controller = data["controllers"]["main"]
        return [
            {
                "controller": controller,
                "ArchitectureModifications": [],
                "StrategyModifications": [],
                "ConnectionModifications": [],
                "connection": data["connection"],
                "asked_for_amount": 0,
                "asked_for_ticker": controller.quote,
                "pair": controller.pair,
                "price": data["candles"][controller]["latest"]["close"],
                "side": SIDES.KEEP,
            },
        ]
