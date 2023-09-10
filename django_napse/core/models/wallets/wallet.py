import time

from django.db import models

from django_napse.core.models.bots.controller import Controller
from django_napse.core.models.connections.connection import Connection
from django_napse.core.models.wallets.currency import Currency
from django_napse.core.models.wallets.managers import WalletManager
from django_napse.utils.errors import WalletError
from django_napse.utils.findable_class import FindableClass


class Wallet(models.Model, FindableClass):
    title = models.CharField(max_length=255, default="Wallet")
    locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WalletManager()

    def __str__(self):
        return f"WALLET: {self.pk=}"

    def info(self, verbose=True, beacon=""):
        self = self.find()
        string = ""
        string += f"{beacon}Wallet ({self.pk=}):\n"
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
    def testing(self):
        return self.owner.testing

    @property
    def space(self):  # pragma: no cover
        error_msg = f"space() not implemented by default. Please implement it in {self.__class__}."
        raise NotImplementedError(error_msg)

    @property
    def exchange_account(self):  # pragma: no cover
        error_msg = "exchange_account() not implemented by default. Please implement in a subclass of Wallet."
        raise NotImplementedError(error_msg)

    def spend(self, amount: float, ticker: str, recv: int = 3, **kwargs) -> None:
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

    def top_up(self, amount: float, ticker: str, mbp: float | None = None, recv: int = 3, **kwargs) -> None:
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
        try:
            currency = self.currencies.get(ticker=ticker)
        except Currency.DoesNotExist:
            return False
        return currency.amount >= amount

    def get_amount(self, ticker: str) -> float:
        try:
            curr = self.currencies.get(ticker=ticker)
        except Currency.DoesNotExist:
            return 0
        return curr.amount

    def value_mbp(self) -> float:
        value = 0
        for currency in self.currencies.all():
            if currency.amount == 0:
                continue
            value += currency.amount * currency.mbp
        return value

    def value_market(self) -> float:
        value = 0
        for currency in self.currencies.all():
            if currency.amount == 0:
                continue
            value += currency.amount * Controller.get_asset_price(exchange_account=self.exchange_account, base=currency.ticker)
        return value

    def to_dict(self):
        currencies = self.currencies.all()
        return {
            "title": self.title,
            "testing": self.testing,
            "locked": self.locked,
            "created_at": self.created_at,
            "currencies": {
                currency.ticker: {
                    "amount": currency.amount,
                    "mbp": currency.mbp,
                }
                for currency in currencies
            },
        }


class SpaceWallet(Wallet):
    owner = models.OneToOneField("NapseSpace", on_delete=models.CASCADE, related_name="wallet")

    @property
    def space(self):
        return self.owner

    @property
    def exchange_account(self):
        return self.space.exchange_account.find()

    def connect_to(self, bot):
        return Connection.objects.create(owner=self, bot=bot)


class SpaceSimulationWallet(Wallet):
    owner = models.OneToOneField("NapseSpace", on_delete=models.CASCADE, related_name="simulation_wallet")

    @property
    def testing(self):
        return True

    @property
    def space(self):
        return self.owner

    @property
    def exchange_account(self):
        return self.space.exchange_account.find()

    def reset(self):
        self.currencies.all().delete()

    def connect_to(self, bot):
        return Connection.objects.create(owner=self, bot=bot)


class OrderWallet(Wallet):
    owner = models.OneToOneField("Order", on_delete=models.CASCADE, related_name="wallet")

    @property
    def exchange_account(self):
        return self.owner.exchange_account.find()


class ConnectionWallet(Wallet):
    owner = models.OneToOneField("Connection", on_delete=models.CASCADE, related_name="wallet")

    @property
    def space(self):
        return self.owner.space

    @property
    def exchange_account(self):
        return self.space.exchange_account.find()
