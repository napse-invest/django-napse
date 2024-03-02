from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from django_napse.core.models.bots.architecture import Architecture
    from django_napse.core.models.bots.controller import Controller
    from django_napse.core.models.bots.plugin import Plugin
    from django_napse.core.models.bots.strategy import Strategy
    from django_napse.core.models.connections.connection import Connection


@dataclass
class TradingDataclass:
    """Represents all the data needed to initiate a trade without having to query the database after this initial call."""

    strategy: "Strategy"
    config: dict[str, any]
    architecture: "Architecture"
    controllers: dict[str, "Controller"]
    connections: list["Connection"]
    connection_data: dict["Connection", dict[str, any]]
    plugins: dict[str, list["Plugin"]]


class CandleDataclass(BaseModel):
    controller: "Controller"
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    extra: dict[str, any]


class CandleDataPydantic(BaseModel):
    candles: dict["Controller":]
