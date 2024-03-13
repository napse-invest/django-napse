from datetime import datetime

from pydantic import BaseModel, PositiveFloat


class CandlePydantic(BaseModel):
    """A Pydantic model for the candles (used for live trading)."""

    open_time: datetime
    open: PositiveFloat
    high: PositiveFloat
    low: PositiveFloat
    close: PositiveFloat
    volume: PositiveFloat
