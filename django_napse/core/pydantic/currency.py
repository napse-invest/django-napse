from pydantic import BaseModel


class CurrencyPydantic(BaseModel):
    """A Pydantic model for the Currency class."""

    ticker: str
    amount: float
    mbp: float
