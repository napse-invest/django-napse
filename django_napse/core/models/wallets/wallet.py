import time
from datetime import datetime
from typing import TYPE_CHECKING

from django.db import models
from pydantic import BaseModel

from django_napse.core.models.bots.controller import Controller
from django_napse.core.models.wallets.currency import Currency, CurrencyPydantic
from django_napse.core.models.wallets.managers import WalletManager
from django_napse.utils.errors import WalletError
from django_napse.utils.findable_class import FindableClass

if TYPE_CHECKING:
    from django_napse.core.models.accounts.exchange import ExchangeAccount
    from django_napse.core.models.accounts.space import Space


class WalletPydantic(BaseModel):
    """A Pydantic model for the Wallet class."""

    title: str
    testing: bool
    locked: bool
    created_at: datetime
    currencies: dict[str, CurrencyPydantic]


class Wallet(models.Model, FindableClass):
    """A Wallet is a collection of currencies."""

    title = models.CharField(max_length=255, default="Wallet")
    locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WalletManager()

    def __str__(self) -> str:  # pragma: no cover
        return f"WALLET: {self.pk=}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        self = self.find()
        string = ""
        string += f"{beacon}Wallet ({self.pk=}):\t{type(self)}\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.title=}\n"
        string += f"{beacon}\t{self.testing=}\n"
        string += f"{beacon}\t{self.locked=}\n"
        string += f"{beacon}Currencies\n"
        if self.currencies.count() == 0:
            string += f"{beacon}\tNo currencies\n"
        else:
            for currency in self.currencies.all():
                string += f"{beacon}\t{currency.ticker}: {currency.amount} @ ${currency.mbp}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def testing(self) -> bool:
        """Return whether the wallet is in testing mode."""
        return self.owner.testing

    @property
    def space(self) -> "Space":  # pragma: no cover
        """Return the space that owns the wallet."""
        error_msg = f"space() not implemented by default. Please implement it in {self.__class__}."
        raise NotImplementedError(error_msg)

    @property
    def exchange_account(self) -> "ExchangeAccount":  # pragma: no cover
        """Return the exchange account that contains the wallet."""
        error_msg = "exchange_account() not implemented by default. Please implement in a subclass of Wallet."
        raise NotImplementedError(error_msg)

    def spend(self, amount: float, ticker: str, recv: int = 3, **kwargs: dict) -> None:
        """Spend an amount of a currency from the wallet.

        Args:
            amount (float): The amount to spend.
            ticker (str): The ticker of the currency to spend.
            recv (int, optional): The time to wait before failing the transaction. Defaults to 3.
            kwargs (dict): Additional arguments.

        Raises:
            WalletError.SpendError: If you try to spend money from the wallet without using the Transactions class.
            ValueError: If the amount is negative.
            TimeoutError: If the wallet is locked for too long.
            WalletError.SpendError: If the currency does not exist in the wallet.
            WalletError.SpendError: If there is not enough money in the wallet.
        """
        if not kwargs.get("force", False):
            error_msg = "DANGEROUS: You should not use this method outside of select circumstances. Use Transactions instead."
            raise WalletError.SpendError(error_msg)

        if amount <= 0:
            error_msg: str = f"Amount must be positive, got {amount}"
            raise ValueError(error_msg)

        start_time = time.time()
        while self.locked:
            time.sleep(0.01)
            if time.time() - start_time > recv:
                error_msg: str = f"Wallet: {self.title} is locked"
                raise TimeoutError(error_msg)
        self.locked = True
        self.save()

        try:
            currency = self.currencies.get(ticker=ticker)
        except Currency.DoesNotExist as err:
            self.locked = False
            self.save()
            error_msg: str = f"Currency {ticker} does not exist in wallet: {self.title}."
            raise WalletError.SpendError(error_msg) from err

        if currency.amount < amount:
            self.locked = False
            self.save()
            error_msg: str = f"Not enough money in wallet: {self.title} ({amount} > {currency.amount} {ticker})."
            raise WalletError.SpendError(error_msg)

        currency.amount -= amount
        currency.save()
        self.locked = False
        self.save()

    def top_up(self, amount: float, ticker: str, mbp: float | None = None, recv: int = 3, **kwargs: dict) -> None:
        """Top up the wallet with an amount of a currency.

        Args:
            amount (float): The amount to top up.
            ticker (str): The ticker of the currency to top up.
            mbp (float, optional): The price of the currency. Defaults to None.
            recv (int, optional): The time to wait before failing the transaction. Defaults to 3.
            kwargs (dict): Additional arguments.

        Raises:
            WalletError.TopUpError: If you try to top up the wallet without using the Transactions class.
            ValueError: If the amount is negative.
            TimeoutError: If the wallet is locked for too long.
        """
        if not kwargs.get("force", False):
            error_msg = "DANGEROUS: You should not use this method outside of select circumstances. Use Transactions instead."
            raise WalletError.TopUpError(error_msg)

        if amount <= 0:
            error_msg: str = f"Amount must be positive, got {amount}"
            raise ValueError(error_msg)

        if mbp is None:
            mbp = Controller.get_asset_price(exchange_account=self.exchange_account, base=ticker)

        start_time = time.time()
        while self.locked:
            time.sleep(0.01)
            if time.time() - start_time > recv:
                error_msg: str = f"Wallet: {self.title} is locked"
                raise TimeoutError(error_msg)

        self.locked = True
        self.save()
        try:
            currency = self.currencies.get(ticker=ticker)
        except Currency.DoesNotExist:
            currency = Currency.objects.create(wallet=self, ticker=ticker, amount=0, mbp=0)
        currency.mbp = (currency.mbp * currency.amount + mbp * amount) / (currency.amount + amount)
        currency.amount += amount
        currency.save()
        self.locked = False
        self.save()

    def has_funds(self, amount: float, ticker: str) -> bool:
        """Check if the wallet has enough funds.

        Args:
            amount (float): The amount the wallet should have.
            ticker (str): The ticker of the currency.

        Returns:
            bool: Whether the wallet has enough funds.
        """
        try:
            currency = self.currencies.get(ticker=ticker)
        except Currency.DoesNotExist:
            return False
        return currency.amount >= amount

    def get_amount(self, ticker: str) -> float:
        """Return the amount of a currency in the wallet.

        Args:
            ticker (str): The ticker of the currency.

        Returns:
            float: The amount of the currency in the wallet.
        """
        try:
            curr = self.currencies.get(ticker=ticker)
        except Currency.DoesNotExist:
            return 0
        return curr.amount

    def value_mbp(self) -> float:
        """Return the value of the wallet in USDT.

        Returns:
            float: The value of the wallet in USDT.
        """
        value = 0
        for currency in self.currencies.all():
            if currency.amount == 0:
                continue
            value += currency.amount * currency.mbp
        return value

    def value_market(self) -> float:
        """Return the value of the wallet in USDT.

        Returns:
            float: The value of the wallet in USDT.
        """
        value = 0
        for currency in self.currencies.all():
            if currency.amount == 0:
                continue
            value += currency.amount * Controller.get_asset_price(exchange_account=self.exchange_account, base=currency.ticker)
        return value

    def to_dict(self) -> WalletPydantic:
        """Return a dictionary representation of the wallet.

        Returns:
            dict: The dictionary representation of the wallet.
        """
        currencies = self.currencies.all()

        return WalletPydantic(
            title=self.title,
            testing=self.testing,
            locked=self.locked,
            created_at=self.created_at,
            currencies={
                currency.ticker: CurrencyPydantic(
                    ticker=currency.ticker,
                    amount=currency.amount,
                    mbp=currency.mbp,
                )
                for currency in currencies
            },
        )
