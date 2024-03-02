from datetime import datetime

from pydantic import BaseModel

from django_napse.core.pydantic.currency import CurrencyPydantic


class WalletPydantic(BaseModel):
    """A Pydantic model for the Wallet class."""

    title: str
    testing: bool
    locked: bool
    created_at: datetime
    currencies: dict[str, CurrencyPydantic]
