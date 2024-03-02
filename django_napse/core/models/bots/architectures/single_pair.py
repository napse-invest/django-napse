from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from binance.helpers import interval_to_milliseconds
from django.db import models
from pytz import UTC

from django_napse.core.models.bots.architecture import Architecture

if TYPE_CHECKING:
    from django_napse.core.models.bots.controller import Controller


class SinglePairArchitecture(Architecture):
    controller = models.ForeignKey("Controller", on_delete=models.CASCADE, related_name="single_pair_architectures")
    variable_last_candle_date = models.DateTimeField(default=datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=UTC))

    def __str__(self) -> str:
        return f"SINGLE PAIR ARCHITECHTURE {self.pk}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}Single Pair Architecture {self.pk}:\n"
        new_beacon = beacon + "\t"
        string += f"{beacon}Controller:\n{beacon}{self.controller.info(beacon=new_beacon, verbose=False)}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    def copy(self):
        return SinglePairArchitecture.objects.create(constants={"controller": self.controller}, variables={})

    def controllers_dict(self) -> dict[str, "Controller"]:
        return {"main": self.controller}

    def skip(self, data: dict) -> bool:
        if data["candles"][data["controllers"]["main"]]["current"]["open_time"] < self.variable_last_candle_date + timedelta(
            milliseconds=interval_to_milliseconds(data["controllers"]["main"].interval),
        ):
            return True
        return False

    def architecture_modifications(self, order: dict, data: dict):
        return [
            {
                "key": "last_candle_date",
                "value": str(data["candles"][data["controllers"]["main"]]["current"]["open_time"]),
                "target_type": "datetime",
                "ignore_failed_order": True,
            },
        ]

    def accepted_tickers(self):
        return [self.controller.base, self.controller.quote]

    def accepted_investment_tickers(self):
        return [self.controller.quote]
