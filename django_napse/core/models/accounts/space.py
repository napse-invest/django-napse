from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from django.db import models
from django.utils.timezone import get_default_timezone

from django_napse.core.models.accounts.managers import SpaceManager
from django_napse.core.models.bots.bot import Bot
from django_napse.core.models.bots.controller import Controller
from django_napse.core.models.fleets.fleet import Fleet
from django_napse.core.models.orders.order import Order
from django_napse.core.models.transactions.credit import Credit
from django_napse.core.models.transactions.debit import Debit
from django_napse.utils.constants import EXCHANGE_TICKERS, STABLECOINS
from django_napse.utils.errors import SpaceError
from django_napse.utils.errors.exchange import ExchangeError
from django_napse.utils.errors.wallets import WalletError

if TYPE_CHECKING:
    from django_napse.core.models.wallets.currency import Currency


class Space(models.Model):
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
        import django_napse.core.models import Space, ExchangeAccount

        exchange_account: ExchangeAccount = ...
        space = Space.objects.create(
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

    objects = SpaceManager()

    class Meta:  # noqa: D106
        unique_together = ("name", "exchange_account")

    def __str__(self) -> str:
        return f"SPACE: {self.name}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
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
        """Return quick value of space's wallet."""
        stablecoins = STABLECOINS.get(self.exchange_account.exchange.name)

        def _add_currency_value(currency: Currency) -> float:
            if currency.ticker in stablecoins:
                return currency.amount
            # controller = Controller.objects.filter(pair=f"{currency.ticker}USDT").first()  # noqa
            controller = Controller.get(exchange_account=self.exchange_account, base=currency.ticker, quote="USDT")
            return controller.get_price() * currency.amount
            # return controller.price * currency.amount

        value = 0

        # Connections values
        connections = self.wallet.connections.all()
        for connection in connections:
            for currency in connection.wallet.currencies.all():
                value += _add_currency_value(currency)

        # Wallet value
        for currency in self.wallet.currencies.all():
            value += _add_currency_value(currency)
        return value

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

    def invest(self, amount: float, ticker: str) -> Credit:
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

    def withdraw(self, amount: float, ticker: str) -> Debit:
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
