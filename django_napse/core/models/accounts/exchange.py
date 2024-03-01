import uuid

from django.db import models

from django_napse.core.models.accounts.managers.exchange import ExchangeAccountManager
from django_napse.utils.constants import EXCHANGE_TICKERS
from django_napse.utils.errors import ExchangeAccountError
from django_napse.utils.findable_class import FindableClass
from django_napse.utils.trading.binance_controller import BinanceController, ExchangeController


class Exchange(models.Model):
    """Represent an exchange entity, like Binance, Kraken, ...."""

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return f"EXCHANGE: {self.name}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return & display info about the exchange."""
        string = ""
        string += f"{beacon}Exchange ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.name=}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string

    def get_tickers(self) -> list[str]:
        """Return a list of available tickers on the exchange."""
        return EXCHANGE_TICKERS.get(self.name, [])


class ExchangeAccount(models.Model, FindableClass):
    """Represent an account on an exchange."""

    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    exchange = models.ForeignKey(
        "Exchange",
        on_delete=models.CASCADE,
        related_name="accounts",
    )
    name = models.CharField(max_length=200)
    testing = models.BooleanField(default=True)
    description = models.TextField()
    default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ExchangeAccountManager()

    def __str__(self) -> str:
        return f"EXCHANGE ACCOUNT ({self.__class__.__name__}): {self.pk=} - {self.name=} - {self.testing=}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return & display info about the exchange account."""
        string = ""
        string += f"{beacon}{self.__class__.__name__} ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.name=}\n"
        string += f"{beacon}\t{self.testing=}\n"
        string += f"{beacon}\t{self.description=}\n"
        exchange_str = self.exchange.info(verbose=False, beacon=f"{beacon}\t")
        string += f"{beacon}Exchange:\n"
        string += f"{beacon}{exchange_str}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string

    def ping(self) -> None:  # pragma: no cover
        """Ping the exchange with apikey to test its validity."""
        error_msg = f"ping() not implemented for {self.__class__.__name__}"
        raise NotImplementedError(error_msg)

    def create_client(self):  # pragma: no cover # noqa
        error_msg = f"create_client() not implemented for {self.__class__.__name__}"
        raise NotImplementedError(error_msg)

    def exchange_controller(self) -> "ExchangeController":  # pragma: no cover # noqa
        error_msg = f"exchange_controller() not implemented for {self.__class__.__name__}"
        raise NotImplementedError(error_msg)

    def get_tickers(self) -> list[str]:
        """Return a list of available tickers on the exchange."""
        return self.exchange.get_tickers()


class BinanceAccount(ExchangeAccount):
    """An exchange account on the Binance exchange."""

    public_key = models.CharField(max_length=200)
    private_key = models.CharField(max_length=200)

    class Meta:  # noqa
        unique_together = ("public_key", "private_key")

    def __str__(self) -> str:
        return "BINANCE " + super().__str__()

    def ping(self) -> None:
        """Ping the exchange with apikey to test its validity."""
        request = self.exchange_controller().get_info()
        if "error" in request:
            error_msg = f"Error pinging {self.exchange.name}. Check that your API keys are correct and have the correct permissions."
            raise ExchangeAccountError.APIPermissionError(error_msg)

    def exchange_controller(self) -> BinanceController:
        """Return the Binance's controller."""
        return BinanceController(self.public_key, self.private_key)


EXCHANGE_ACCOUNT_DICT = {
    "BINANCE": BinanceAccount,
}
