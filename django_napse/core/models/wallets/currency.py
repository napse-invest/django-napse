from typing import TYPE_CHECKING

from django.db import models
from pydantic import BaseModel

if TYPE_CHECKING:
    from django_napse.core.models.wallets.wallet import Wallet


class CurrencyPydantic(BaseModel):
    """A Pydantic model for the Currency class."""

    ticker: str
    amount: float
    mbp: float


class Currency(models.Model):
    """A Currency contains the amount of a ticker in a wallet, as well as the Mean Buy Price (MBP)."""

    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE, related_name="currencies")
    mbp = models.FloatField()
    ticker = models.CharField(max_length=10)
    amount = models.FloatField(default=0)

    class Meta:  # noqa
        unique_together = ("wallet", "ticker")

    def __str__(self) -> str:  # pragma: no cover
        return f"CURRENCY {self.pk}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the history information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}Currency ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.wallet=}\n"
        string += f"{beacon}\t{self.mbp=}\n"
        string += f"{beacon}\t{self.ticker=}\n"
        string += f"{beacon}\t{self.amount=}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def testing(self) -> bool:
        """Return the testing status of the wallet."""
        return self.wallet.testing

    def copy(self, owner: "Wallet") -> "Currency":
        """Return a copy of the currency with a new owner."""
        return Currency.objects.create(
            wallet=owner,
            mbp=self.mbp,
            ticker=self.ticker,
            amount=self.amount,
        )
