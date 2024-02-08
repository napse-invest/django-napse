import uuid
from datetime import datetime, timedelta

from django.db import models
from django.utils.timezone import get_default_timezone

from django_napse.core.models.accounts.managers import NapseSpaceManager
from django_napse.core.models.bots.bot import Bot
from django_napse.core.models.fleets.fleet import Fleet
from django_napse.core.models.orders.order import Order
from django_napse.core.models.transactions.credit import Credit
from django_napse.core.models.transactions.debit import Debit
from django_napse.utils.constants import EXCHANGE_TICKERS
from django_napse.utils.errors import SpaceError
from django_napse.utils.errors.exchange import ExchangeError
from django_napse.utils.errors.wallets import WalletError


class NapseSpace(models.Model):
    """Categorize and manage money.

    Attributes:
        name: Name of the space.
        uuid: Unique identifier of the space.
        description: Description of the space.
        exchange_account: Exchange account of the space.
        created_at: Date of creation of the space.


    Examples:
        Create a space:
        ```python
        import django_napse.core.models import NapseSpace, ExchangeAccount

        exchange_account: ExchangeAccount = ...
        space = NapseSpace.objects.create(
            name="Space",
            description="Space description",
            exchange_account=exchange_account,
        )
        ```
    """

    name = models.CharField(max_length=200)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    description = models.TextField()
    exchange_account = models.ForeignKey("ExchangeAccount", on_delete=models.CASCADE, related_name="spaces")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = NapseSpaceManager()

    class Meta:
        unique_together = ("name", "exchange_account")

    def __str__(self):
        return f"SPACE: {self.name}"

    def info(self, verbose: bool = True, beacon: str = "") -> str:
        """Info documentation.

        Params:
            verbose: Print to console.
            beacon: Indentation for printing.
        """
        string = ""
        string += f"{beacon}Space ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.name=}\n"
        string += f"{beacon}\t{self.uuid=}\n"
        string += f"{beacon}Exchange Account:\n"
        new_beacon = beacon + "\t"
        string += f"{self.exchange_account.info(verbose=False, beacon=new_beacon)}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def testing(self) -> bool:
        """Testing property."""
        return self.exchange_account.testing

    @property
    def value(self) -> float:
        """Value market of space's wallet."""
        connections = self.wallet.connections.all()
        return sum([connection.wallet.value_market() for connection in connections])

    @property
    def fleets(self) -> models.QuerySet:
        """Fleets of the space."""
        connections = self.wallet.connections.all()
        return Fleet.objects.filter(clusters__links__bot__connections__in=connections).distinct()

    @property
    def bots(self) -> models.QuerySet:
        """Bots of the space."""
        connections = self.wallet.connections.all()
        return Bot.objects.filter(connections__in=connections)

    def get_stats(self) -> dict[str, int | float | str]:
        """Statistics of space."""
        order_count_30 = Order.objects.filter(
            connection__in=self.wallet.connections.all(),
            created_at__gt=datetime.now(tz=get_default_timezone()) - timedelta(days=30),
        ).count()

        return {
            "value": self.value,
            "order_count_30": order_count_30,
            "delta_30": 0,  # need history on space's value
        }

    def delete(self) -> None:
        """Delete space."""
        if self.testing:
            return super().delete()
        if self.value > 0:
            raise SpaceError.DeleteError
        return super().delete()

    def invest(self, amount: float, ticker: str):
        """Invest in space."""
        if ticker not in EXCHANGE_TICKERS.get("BINANCE"):
            error_msg: str = f"{ticker} is not available on {self.exchange_account.name} exchange."
            raise ExchangeError.UnavailableTicker(error_msg)

        # Real invest
        if not self.testing:
            error_msg: str = "Investing for real is not available yet."
            raise NotImplementedError(error_msg)

        # Testing invest
        Credit.objects.create(wallet=self.wallet, amount=amount, ticker=ticker)

    def withdraw(self, amount: float, ticker: str):
        """Withdraw from space."""
        if ticker not in [currency.ticker for currency in self.wallet.currencies.all()]:
            error_msg: str = f"{ticker} is not on your {self.name}(space)'s wallet."
            raise WalletError.UnavailableTicker(error_msg)

        # Real withdraw
        if not self.testing:
            error_msg: str = "Withdrawing for real is not available yet."
            raise NotImplementedError(error_msg)

        # Testing withdraw
        Debit.objects.create(
            wallet=self.wallet,
            amount=amount,
            ticker=ticker,
        )
