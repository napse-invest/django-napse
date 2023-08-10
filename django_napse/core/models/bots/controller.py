import math
from datetime import datetime, timedelta, timezone

from django.db import models
from requests.exceptions import ConnectionError, ReadTimeout, SSLError

from django_napse.core.models.bots.managers.controller import ControllerManager
from django_napse.utils.constants import EXCHANGE_INTERVALS, EXCHANGE_PAIRS, STABLECOINS
from django_napse.utils.errors import ControllerError
from django_napse.utils.trading.binance_controller import BinanceController


class Controller(models.Model):
    exchange_account = models.ForeignKey("ExchangeAccount", on_delete=models.CASCADE, related_name="controller")

    pair = models.CharField(max_length=10)
    base = models.CharField(max_length=10)
    quote = models.CharField(max_length=10)
    interval = models.CharField(max_length=10)

    min_notional = models.FloatField(null=True)
    min_trade = models.FloatField(null=True)
    lot_size = models.IntegerField(null=True)
    price = models.FloatField(null=True)
    last_price_update = models.DateTimeField(null=True)
    last_settings_update = models.DateTimeField(null=True)

    objects = ControllerManager()

    class Meta:
        unique_together = ("pair", "interval", "exchange_account")

    def __str__(self):
        return f"Controller {self.pair} - {self.interval}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.base = self.base.upper()
            self.quote = self.quote.upper()
            if self.base == self.quote:
                error_msg = f"Base and quote cannot be the same: {self.base} - {self.quote}"
                raise ControllerError.InvalidSetting(error_msg)
            self.pair = self.base + self.quote
            self._update_variables()
            if self.interval not in EXCHANGE_INTERVALS[self.exchange.name]:
                error_msg = f"Invalid interval: {self.interval}"
                raise ControllerError.InvalidSetting(error_msg)
        return super().save(*args, **kwargs)

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Controller {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.pair=}\n"
        string += f"{beacon}\t{self.base=}\n"
        string += f"{beacon}\t{self.quote=}\n"
        string += f"{beacon}\t{self.interval=}\n"
        string += f"{beacon}\t{self.min_notional=}\n"
        string += f"{beacon}\t{self.min_trade=}\n"
        string += f"{beacon}\t{self.lot_size=}\n"
        string += f"{beacon}\t{self.price=}\n"
        string += f"{beacon}\t{self.last_price_update=}\n"
        string += f"{beacon}\t{self.last_settings_update=}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    @staticmethod
    def get(exchange_account, base: str, quote: str, interval: str = "1m") -> "Controller":
        """Return a controller object from the database."""
        try:
            controller = Controller.objects.get(
                exchange_account=exchange_account,
                base=base,
                quote=quote,
                interval=interval,
            )
        except Controller.DoesNotExist:
            controller = Controller.objects.create(
                exchange_account=exchange_account,
                base=base,
                quote=quote,
                interval=interval,
                bypass=True,
            )
        controller.update_variables()
        return controller

    @property
    def exchange_controller(self):
        return self.exchange_account.find().exchange_controller()

    @property
    def exchange(self):
        return self.exchange_account.exchange

    def update_variables(self) -> None:
        """If the variables are older than 1 minute, update them."""
        if self.last_settings_update is None or self.last_settings_update < datetime.now(tz=timezone.utc) - timedelta(minutes=1):
            self._update_variables()

    def _update_variables(self) -> None:
        """Update the variables of the controller."""
        exchange_controller = self.exchange_controller

        if exchange_controller == "DEFAULT":
            pass
        elif exchange_controller.__class__ == BinanceController:
            try:
                filters = exchange_controller.client.get_symbol_info(self.pair)["filters"]
                last_price = exchange_controller.client.get_ticker(symbol=self.pair)["lastPrice"]
                for specific_filter in filters:
                    if specific_filter["filterType"] == "LOT_SIZE":
                        self.lot_size = -int(math.log10(float(specific_filter["stepSize"])))
                    if specific_filter["filterType"] in ["MIN_NOTIONAL", "NOTIONAL"]:
                        self.min_notional = float(specific_filter["minNotional"])
                self.min_trade = self.min_notional / float(last_price)
                self.last_settings_update = datetime.now(tz=timezone.utc)
            except ReadTimeout:
                print("ReadTimeout in _update_variables")
            except SSLError:
                print("SSLError in _update_variables")
            except ConnectionError:
                print("ConnectionError in _update_variables")
            except Exception as e:
                print(f"Exception in _update_variables: {e}, {type(e)}")
        else:
            error_msg = f"Exchange controller not supported: {exchange_controller.__class__}"
            raise NotImplementedError(error_msg)

        if self.pk:
            self.save()

    def send_candles_to_bots(self, closed_candle, current_candle) -> list:
        """Scan all bots (that are allowed to trade) and get their orders.

        Args:
        ----
        closed_candle (dict): The candle that just closed.
        current_candle (dict): The candle that is currently open.

        Returns:
        -------
        list: A list of orders.
        """
        orders = []
        for bot in self.bots.all().filter(is_simulation=False, fleet__running=True, can_trade=True):
            bot = bot.find()
            orders.append(bot.give_order(closed_candle, current_candle))
        return orders

    @staticmethod
    def get_asset_price(exchange_account, base: str, quote: str = "USDT") -> float:
        """Get the price of an asset."""
        if base in STABLECOINS[exchange_account.exchange.name]:
            return 1
        if base + quote not in EXCHANGE_PAIRS[exchange_account.exchange.name]:
            error_msg = f"Invalid pair: {base+quote} on {exchange_account.exchange.name}"
            raise ControllerError.InvalidPair(error_msg)
        controller = Controller.get(exchange_account=exchange_account, base=base, quote=quote, interval="1m")

        return float(controller.get_price())

    def _get_price(self) -> float:
        """Get the price of the pair.

        Always calls the exchange API. (Can be costly)

        Returns
        -------
        float: The price of the pair.
        """
        exchange_controller = self.exchange_controller
        if exchange_controller.__class__ == BinanceController:
            try:
                self.price = float(exchange_controller.client.get_ticker(symbol=self.pair)["lastPrice"])
                self.last_price_update = datetime.now(tz=timezone.utc)
            except ReadTimeout:
                print("ReadTimeout in _get_price")
            except SSLError:
                print("SSLError in _get_price")
            except ConnectionError:
                print("ConnectionError in _get_price")
            except Exception as e:
                print(f"Exception in _get_price: {e}, {type(e)}")
        else:
            error_msg = f"Exchange controller not supported: {exchange_controller.__class__}"
            raise NotImplementedError(error_msg)
        self.save()

    def get_price(self) -> float:
        """Retreive the price of the pair.

        Only updates the price if it is older than 1 minute.

        Returns
        -------
        float: The price of the pair.
        """
        if self.last_price_update is None or self.last_price_update < datetime.now(tz=timezone.utc) - timedelta(minutes=1):
            self._get_price()
        return self.price

    def download(
        self,
        start_date: datetime,
        end_date: datetime,
        squash: bool = False,
        verbose: int = 0,
    ):
        return self.exchange_controller.download(
            controller=self,
            start_date=start_date,
            end_date=end_date,
            squash=squash,
            verbose=verbose,
        )


class Candle(models.Model):
    controller = models.ForeignKey("Controller", on_delete=models.CASCADE, related_name="candles")
    latest = models.BooleanField(default=False)
    last_update = models.DateTimeField(auto_now=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()

    def __str__(self):
        return f"CANDLE {self.pk}"
