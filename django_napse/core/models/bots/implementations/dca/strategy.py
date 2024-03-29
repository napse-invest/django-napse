from django.db import models

from django_napse.core.models.bots.architectures.single_pair import SinglePairArchitecture
from django_napse.core.models.bots.implementations.dca.config import DCABotConfig
from django_napse.core.models.bots.strategy import Strategy
from django_napse.utils.constants import SIDES


class DCAStrategy(Strategy):
    """Implementation of a simple Dollar Cost Averaging strategy."""

    variable_last_buy_date = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"DCA BOT STRATEGY: {self.pk=}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}Strategy ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.config=}\n"
        string += f"{beacon}\t{self.architecture=}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string

    @classmethod
    def config_class(cls) -> type[DCABotConfig]:
        """Return the config class for this strategy."""
        return DCABotConfig

    @classmethod
    def architecture_class(cls) -> type[SinglePairArchitecture]:
        """Return the architecture class for this strategy."""
        return SinglePairArchitecture

    def give_order(self, data: dict) -> list[dict]:
        """Trading logic for the DCA strategy."""
        controller = data["controllers"]["main"]
        if (
            self.variable_last_buy_date is None
            or data["candles"][controller]["current"].open_time - self.variable_last_buy_date >= data["config"]["timeframe"]
        ):
            return [
                {
                    "controller": controller,
                    "ArchitectureModifications": [],
                    "StrategyModifications": [
                        {
                            "key": "last_buy_date",
                            "value": str(data["candles"][controller]["current"].open_time),
                            "target_type": "datetime",
                            "ignore_failed_order": False,
                        },
                    ],
                    "ConnectionModifications": [],
                    "connection": data["connection"],
                    "asked_for_amount": 20,
                    "asked_for_ticker": controller.quote,
                    "pair": controller.pair,
                    "price": data["candles"][controller]["latest"].close,
                    "side": SIDES.BUY,
                },
            ]
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
                "price": data["candles"][controller]["latest"].close,
                "side": SIDES.KEEP,
            },
        ]
