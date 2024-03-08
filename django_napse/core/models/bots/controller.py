import math
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Optional

from django.db import models
from requests.exceptions import ConnectionError, ReadTimeout, SSLError

from django_napse.core.models.bots.managers.controller import ControllerManager
from django_napse.core.models.orders.order import Order, OrderBatch
from django_napse.utils.constants import EXCHANGE_INTERVALS, EXCHANGE_PAIRS, ORDER_STATUS, SIDES, STABLECOINS
from django_napse.utils.errors import ControllerError
from django_napse.utils.trading.binance_controller import BinanceController, ExchangeController

if TYPE_CHECKING:
    from django_napse.core.models.accounts.exchange import Exchange, ExchangeAccount
    from django_napse.core.models.bots.bot import Bot


class Controller(models.Model):
    """Model to control the trading of a pair on an exchange."""

    exchange_account: "ExchangeAccount" = models.ForeignKey("ExchangeAccount", on_delete=models.CASCADE, related_name="controller")

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

    class Meta:  # noqa: D106
        unique_together = ("pair", "interval", "exchange_account")

    def __str__(self) -> str:
        return f"Controller {self.pair} (id: {self.pk})"

    def save(self, *args: list[any], **kwargs: dict[str, any]) -> None:
        """Save the instance."""
        if not self.pk:
            self.base = self.base.upper()
            self.quote = self.quote.upper()
            if self.base == self.quote:
                error_msg = f"Base and quote cannot be the same: {self.base} - {self.quote}"
                raise ControllerError.InvalidSetting(error_msg)
            self.pair = self.base + self.quote
            self.update_variables_always()
            if self.interval not in EXCHANGE_INTERVALS[self.exchange.name]:
                error_msg = f"Invalid interval: {self.interval}"
                raise ControllerError.InvalidSetting(error_msg)
        return super().save(*args, **kwargs)

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
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
    def get(exchange_account: "ExchangeAccount", base: str, quote: str, interval: str = "1m") -> "Controller":
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
    def exchange_controller(self) -> "ExchangeController":
        """Return the exchange controller of the controller.

        Returns:
            ExchangeController: The exchange controller of the controller.
        """
        return self.exchange_account.find().exchange_controller()

    @property
    def exchange(self) -> "Exchange":
        """Return the exchange of the controller."""
        return self.exchange_account.exchange

    def update_variables(self) -> None:
        """If the variables are older than 1 minute, update them."""
        if self.last_settings_update is None or self.last_settings_update < datetime.now(tz=timezone.utc) - timedelta(minutes=1):
            self.update_variables_always()

    def update_variables_always(self) -> None:
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
                print("ReadTimeout in update_variables_always")
            except SSLError:
                print("SSLError in update_variables_always")
            except ConnectionError:
                print("ConnectionError in update_variables_always")
        else:
            error_msg = f"Exchange controller not supported: {exchange_controller.__class__}"
            raise NotImplementedError(error_msg)

        if self.pk:
            self.save()

    def process_orders(self, no_db_data: Optional[dict] = None, *, testing: bool) -> list[Order]:
        in_simulation = no_db_data is not None
        no_db_data = no_db_data or {
            "buy_orders": Order.objects.filter(
                order__batch__status=ORDER_STATUS.READY,
                order__side=SIDES.BUY,
                order__batch__controller=self,
                order__testing=testing,
            ),
            "sell_orders": Order.objects.filter(
                order__batch__status=ORDER_STATUS.READY,
                order__side=SIDES.SELL,
                order__batch__controller=self,
                order__testing=testing,
            ),
            "keep_orders": Order.objects.filter(
                order__batch__status=ORDER_STATUS.READY,
                order__side=SIDES.KEEP,
                order__batch__controller=self,
                order__testing=testing,
            ),
            "batches": OrderBatch.objects.filter(status=ORDER_STATUS.READY, batch__controller=self),
            "exchange_controller": self.exchange_controller,
            "min_trade": self.min_trade,
            "price": self.get_price(),
        }

        aggregated_order = {
            "buy_amount": 0,
            "sell_amount": 0,
            "min_trade": no_db_data["min_trade"],
            "price": no_db_data["price"],
            "min_notional": self.min_notional,
            "pair": self.pair,
        }

        for order in no_db_data["buy_orders"]:
            aggregated_order["buy_amount"] += order.asked_for_amount
        for order in no_db_data["sell_orders"]:
            aggregated_order["sell_amount"] += order.asked_for_amount

        if aggregated_order["buy_amount"] > 0:
            for order in no_db_data["buy_orders"]:
                order.calculate_batch_share(total=aggregated_order["buy_amount"])
        if aggregated_order["sell_amount"] > 0:
            for order in no_db_data["sell_orders"]:
                order.calculate_batch_share(total=aggregated_order["sell_amount"])
        for order in no_db_data["keep_orders"]:
            order.batch_share = 0

        receipt, executed_amounts_buy, executed_amounts_sell, fees_buy, fees_sell = no_db_data["exchange_controller"].submit_order(
            controller=self,
            aggregated_order=aggregated_order,
            testing=in_simulation or testing,
        )
        all_orders = []
        for order in no_db_data["buy_orders"]:
            order.calculate_exit_amounts(
                controller=self,
                executed_amounts=executed_amounts_buy,
                fees=fees_buy,
            )
            all_orders.append(order)
        for order in no_db_data["sell_orders"]:
            order.calculate_exit_amounts(
                controller=self,
                executed_amounts=executed_amounts_sell,
                fees=fees_sell,
            )
            all_orders.append(order)
        for order in no_db_data["keep_orders"]:
            order.calculate_exit_amounts(
                controller=self,
                executed_amounts={},
                fees={},
            )
            all_orders.append(order)

        for batch in no_db_data["batches"]:
            batch._set_status_post_process(receipt=receipt)

        return all_orders

    def apply_orders(self, orders):
        for order in orders:
            order.save()
            order.apply_swap()

    def send_candles_to_bots(self, closed_candle, current_candle) -> list:
        """Scan all bots (that are allowed to trade) and get their orders.

        Args:
        ----
        closed_candle : The candle that just closed.
        current_candle : The candle that is currently open.

        Returns:
        -------
        list: A list of orders.
        """
        orders = []
        for bot in self.bots.all().filter(is_simulation=False, fleet__running=True, can_trade=True):
            bot: "Bot"
            orders = [*orders, bot.give_order(closed_candle, current_candle)]
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

    def get_price_always(self) -> float:
        """Get the price of the pair.

        Always calls the exchange API. (Can be costly)

        Returns:
        float: The price of the pair.
        """
        exchange_controller = self.exchange_controller
        if exchange_controller.__class__ == BinanceController:
            try:
                self.price = float(exchange_controller.client.get_ticker(symbol=self.pair)["lastPrice"])
                self.last_price_update = datetime.now(tz=timezone.utc)
            except ReadTimeout:
                print("ReadTimeout in get_price_always")
            except SSLError:
                print("SSLError in get_price_always")
            except ConnectionError:
                print("ConnectionError in get_price_always")
        else:
            error_msg = f"Exchange controller not supported: {exchange_controller.__class__}"
            raise NotImplementedError(error_msg)
        self.save()
        return self.price

    def get_price(self) -> float:
        """Retreive the price of the pair.

        Only updates the price if it is older than 1 minute.
        The ControllerUpdate task automaticaly refreshes price data.

        Returns:
            price: The price of the pair.
        """
        if self.last_price_update is None or self.last_price_update < datetime.now(tz=timezone.utc) - timedelta(minutes=1):
            self.get_price_always()
        return self.price

    def download(
        self,
        start_date: datetime,
        end_date: datetime,
        verbose: int = 0,
        *,
        squash: bool = False,
    ):
        return self.exchange_controller.download(
            controller=self,
            start_date=start_date,
            end_date=end_date,
            squash=squash,
            verbose=verbose,
        )
