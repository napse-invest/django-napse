import math

from django.db import models

from django_napse.core.models.bots.architectures.single_pair import SinglePairArchitecture
from django_napse.core.models.bots.implementations.turbo_dca.config import TurboDCABotConfig
from django_napse.core.models.bots.plugins import LBOPlugin, MBPPlugin, SBVPlugin
from django_napse.core.models.bots.strategy import Strategy
from django_napse.core.models.wallets.currency import CurrencyPydantic
from django_napse.utils.constants import SIDES


class TurboDCAStrategy(Strategy):
    variable_last_buy_date = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"TURBO DCA BOT STRATEGY: {self.pk=}"

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
        return TurboDCABotConfig

    @classmethod
    def architecture_class(cls):
        return SinglePairArchitecture

    @classmethod
    def plugin_classes(cls):
        return [MBPPlugin, LBOPlugin, SBVPlugin]

    def give_order(self, data: dict) -> list[dict]:
        controller = data["controllers"]["main"]
        if (
            self.variable_last_buy_date is None
            or data["candles"][controller]["current"]["open_time"] - self.variable_last_buy_date >= data["config"]["timeframe"]
        ):
            mbp = data["connection_data"][data["connection"]]["connection_specific_args"]["mbp"].get_value()
            lbo = data["connection_data"][data["connection"]]["connection_specific_args"]["lbo"].get_value()
            sbv = data["connection_data"][data["connection"]]["connection_specific_args"]["sbv"].get_value()
            available_base = (
                data["connection_data"][data["connection"]]["wallet"]
                .currencies.get(controller.base, CurrencyPydantic(ticker=controller.base, amount=0, mbp=0))
                .amount
            )
            available_quote = (
                data["connection_data"][data["connection"]]["wallet"]
                .currencies.get(controller.quote, CurrencyPydantic(ticker=controller.quote, amount=0, mbp=0))
                .amount
            )
            mbp = mbp if mbp is not None else math.inf
            sbv = sbv if sbv is not None else available_quote
            current_price = data["candles"][controller]["latest"]["close"]
            amount = data["config"]["percentage"] * sbv / 100
            if lbo == 0 or current_price < mbp:
                return [
                    {
                        "controller": controller,
                        "ArchitectureModifications": [],
                        "StrategyModifications": [
                            {
                                "key": "last_buy_date",
                                "value": str(data["candles"][controller]["current"]["open_time"]),
                                "target_type": "datetime",
                                "ignore_failed_order": False,
                            },
                        ],
                        "ConnectionModifications": [],
                        "connection": data["connection"],
                        "asked_for_amount": amount,
                        "asked_for_ticker": controller.quote,
                        "pair": controller.pair,
                        "price": data["candles"][controller]["latest"]["close"],
                        "side": SIDES.BUY,
                    },
                ]
            if current_price > mbp:
                return [
                    {
                        "controller": controller,
                        "ArchitectureModifications": [],
                        "StrategyModifications": [
                            {
                                "key": "last_buy_date",
                                "value": str(data["candles"][controller]["current"]["open_time"]),
                                "target_type": "datetime",
                                "ignore_failed_order": False,
                            },
                        ],
                        "ConnectionModifications": [],
                        "connection": data["connection"],
                        "asked_for_amount": available_base,
                        "asked_for_ticker": controller.base,
                        "pair": controller.pair,
                        "price": data["candles"][controller]["latest"]["close"],
                        "side": SIDES.SELL,
                    },
                ]
            return [
                {
                    "controller": controller,
                    "ArchitectureModifications": [],
                    "StrategyModifications": [
                        {
                            "key": "last_buy_date",
                            "value": str(data["candles"][controller]["current"]["open_time"]),
                            "target_type": "datetime",
                            "ignore_failed_order": False,
                        },
                    ],
                    "ConnectionModifications": [],
                    "connection": data["connection"],
                    "asked_for_amount": 0,
                    "asked_for_ticker": controller.quote,
                    "pair": controller.pair,
                    "price": data["candles"][controller]["latest"]["close"],
                    "side": SIDES.KEEP,
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
                "price": data["candles"][controller]["latest"]["close"],
                "side": SIDES.KEEP,
            },
        ]
