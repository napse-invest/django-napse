import shutil
import time
from datetime import datetime, timedelta, timezone
from time import sleep

import binance.enums as binance_enums
from binance.client import Client
from binance.enums import HistoricalKlinesType
from binance.exceptions import BinanceAPIException
from binance.helpers import convert_ts_str, interval_to_milliseconds
from django.apps import apps
from pytz import UTC
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout

from django_napse.utils.constants import DEFAULT_TAX, DOWNLOAD_STATUS, SIDES
from django_napse.utils.usefull_functions import round_down, round_up


class ExchangeController:
    pass


class BinanceController(ExchangeController):
    """Commmunication interface with binance account."""

    def __init__(self, public_key, private_key):
        client_created = False
        retries = 0
        while not client_created:
            try:
                self.client = Client(public_key, private_key)
                client_created = True
            except ConnectTimeout:
                print(f"ConnectionTimout error while creating client (try: {retries}), retrying...")
                time.sleep(1)
            except ConnectionError:
                print(f"ConnectionError error while creating client (try: {retries}), retrying...")
                time.sleep(1)
            except ReadTimeout:
                print(f"ReadTimeout error while creating client (try: {retries}), retrying...")
                time.sleep(1)
            else:
                if retries > 0:
                    print(f"Client created after {retries} retries.")
            retries += 1

        self.client.get_historical_klines = self._get_historical_klines
        self.client._historical_klines = self._historical_klines
        self.nb_retry: int = 3
        self.recv: int = 5000

    def get_info(self) -> dict:
        """Get the data of the binance account."""
        meter = 0
        while meter < self.nb_retry:
            meter += 1
            try:
                return self.client.get_account(recvWindow=self.recv)
            except ReadTimeout:
                continue
            except BinanceAPIException:
                continue

        return {"error": 408}

    def get_balance(self, ticker: str) -> dict:
        """Return balance of the selected ticker."""
        meter = 0
        while meter < self.nb_retry:
            meter += 1
            try:
                return self.client.get_asset_balance(asset=ticker.upper(), recvWindow=self.recv)
            except ReadTimeout:
                continue
            except BinanceAPIException:
                continue
        return {"error": 408}

    def get_tickers(self) -> list[dict]:
        """Return all available tickers."""
        meter = 0
        while meter < self.nb_retry:
            meter += 1
            try:
                return self.client.get_all_tickers()

            except ConnectionError:
                continue
        return [{"error": 408}]

    def buy_market(self, pair: str, quantity: float) -> dict:
        """Place a spot buy market order.

        !!! WARNING: quantity is in base currency !!!
        """
        Controller = apps.get_model("django_napse_core", "Controller")
        meter = 0
        while meter < self.nb_retry:
            meter += 1

            _, current_candle = Controller.get_candles(pair, "1m")
            price = current_candle["C"]
            quantity = quantity / price
            try:
                order = self.client.order_market_buy(symbol=pair.upper(), quantity=quantity, recvWindow=self.recv)
            except BinanceAPIException:
                continue
            else:
                return order
        return {"error": 408}

    def sell_market(self, pair: str, quantity: float) -> dict:
        """Place a sell market order.

        !!! WARNING: quantity is in quote currency !!!
        """
        meter = 0
        while meter < self.nb_retry:
            meter += 1

            try:
                order = self.client.order_market_sell(symbol=pair.upper(), quantity=quantity, recvWindow=self.recv)
            except BinanceAPIException:
                continue
            else:
                return order
        return {"error": 408}

    def test_market_order(self, pair: str, quantity: float, side_buy: bool = True) -> dict:
        """Simulate a binance order."""
        side = binance_enums.SIDE_BUY if side_buy else binance_enums.SIDE_SELL

        return self.client.create_test_order(
            symbol=pair.upper(),
            side=side,
            type=binance_enums.ORDER_TYPE_MARKET,
            quantity=quantity,
            # price = price,
            recvWindow=self.recv,
        )

    def get_historical_klines(
        self,
        dataset,
        start: datetime,
        end: datetime,
        pair: str,
        interval: str = "1m",
        limit: int = 1000,
        verbose: int = 0,
    ) -> None:
        start_str = str(start)
        end_str = str(end)

        self.client.get_historical_klines(
            pair=pair,
            interval=interval,
            start_str=start_str,
            end_str=end_str,
            limit=limit,
            dataset=dataset,
            verbose=verbose,
        )

    def _get_historical_klines(
        self,
        pair,
        interval,
        dataset,
        start_str,
        end_str,
        limit=1000,
        klines_type: HistoricalKlinesType = HistoricalKlinesType.SPOT,
        verbose: int = 0,
    ):
        dataset.completion = 0
        dataset.set_downloading()
        dataset.save()

        klines = self._historical_klines(
            pair=pair,
            interval=interval,
            start_str=start_str,
            end_str=end_str,
            limit=limit,
            klines_type=klines_type,
            dataset=dataset,
            verbose=verbose,
        )

        dataset.completion = 100
        dataset.set_idle()
        dataset.save()
        return klines

    def _historical_klines(
        self,
        pair,
        interval,
        dataset,
        start_str=None,
        end_str=None,
        limit=1000,
        klines_type: HistoricalKlinesType = HistoricalKlinesType.SPOT,
        verbose: int = 0,
    ):
        Candle = apps.get_model("django_napse_simulations", "Candle")

        output_data = []

        timeframe = interval_to_milliseconds(interval)

        start_ts = convert_ts_str(start_str)
        if start_ts is not None:
            first_valid_ts = self.client._get_earliest_valid_timestamp(pair, interval, klines_type)
            start_ts = max(start_ts, first_valid_ts)

        end_ts = convert_ts_str(end_str)
        total_loops = int(round_up((end_ts - start_ts) / limit / timeframe, 0))
        if end_ts and start_ts and end_ts <= start_ts:
            return output_data

        idx = 0
        start_time = time.time()
        last_percentage_saved = 0

        dataset.save()

        while True:
            found = False
            while not found:
                try:
                    temp_data = self.client._klines(
                        klines_type=klines_type,
                        symbol=pair,
                        interval=interval,
                        limit=limit,
                        startTime=start_ts,
                        endTime=end_ts,
                    )
                    found = True
                except ReadTimeout:
                    time.sleep(1)
                except ConnectionError:
                    time.sleep(1)
            dataset.create_candles(
                [
                    Candle(
                        dataset=dataset,
                        open_time=datetime.fromtimestamp(float(candle[0]) // 1000, tz=timezone.utc),
                        open=float(candle[1]),
                        high=float(candle[2]),
                        low=float(candle[3]),
                        close=float(candle[4]),
                        volume=float(candle[5]),
                    )
                    for candle in temp_data
                ],
            )

            idx += 1
            current_time = time.time()
            eta = (total_loops - idx) * (current_time - start_time) / idx
            eta = timedelta(seconds=eta)
            if verbose > 0:
                elapsed = timedelta(seconds=current_time - start_time)
                progress_str = f"Progress: {idx/total_loops*100:.2f} %"
                eta_str = f" (eta: {eta} s)"
                elapsed_str = f"  (elapsed: {elapsed})"
                loop_str = f" | Loop {idx}/{total_loops} completed"
                loop_size_str = f" | Loop size: {limit} candles."
                columns, rows = shutil.get_terminal_size()
                full_str = ""
                if columns <= len(progress_str):
                    pass
                elif columns <= len(progress_str + eta_str):
                    full_str = progress_str
                elif columns <= len(progress_str + eta_str + elapsed_str):
                    full_str = progress_str + eta_str
                elif columns <= len(progress_str + eta_str + elapsed_str + loop_str):
                    full_str = progress_str + eta_str + elapsed_str
                elif columns <= len(progress_str + eta_str + elapsed_str + loop_str + loop_size_str):
                    full_str = progress_str + eta_str + elapsed_str + loop_str
                else:
                    full_str = progress_str + eta_str + elapsed_str + loop_str + loop_size_str
                full_str += " " * (columns - len(full_str)) + "\r"
                print(full_str, end="")

            percentage = idx / total_loops * 100
            if percentage - last_percentage_saved > 0.1:
                last_percentage_saved = percentage
                dataset.completion = percentage
                dataset.last_update = datetime.now(tz=timezone.utc)
                dataset.eta = eta
                dataset.save()

            if not len(temp_data) or len(temp_data) < limit:
                break

            start_ts = temp_data[-1][0] + timeframe
            if end_ts and start_ts >= end_ts:
                break

        if verbose > 0:
            print()
        return output_data

    def fill_dataset(self, start_date, end_date, dataset, batch_size: int = 1000, verbose: int = 0):
        """Fill the dataset with historical data from the exchange."""
        if verbose > 1:
            print(
                f"### Starting to download: Dataset: pair={dataset.controller.pair}, interval={dataset.controller.interval}\n",
                f"\tstart={start_date}, end={end_date}",
                sep="",
            )
        self.get_historical_klines(
            start=start_date,
            end=end_date,
            pair=dataset.controller.pair,
            interval=dataset.controller.interval,
            limit=batch_size,
            dataset=dataset,
            verbose=verbose,
        )
        return dataset

    def download(
        self,
        controller,
        start_date: datetime,
        end_date: datetime,
        verbose: int = 0,
        *,
        squash: bool = False,
    ):
        """Download all the missing data to complete the dataset."""
        DataSet = apps.get_model("django_napse_simulations", "DataSet")

        start_time = datetime.now(tz=UTC)

        if end_date.second + end_date.microsecond != 0:
            end_date = end_date.replace(second=0, microsecond=0)
            end_date -= timedelta(microseconds=1)

        dataset = DataSet.objects.get(controller=controller)

        if datetime.now(tz=UTC) - dataset.last_update > timedelta(minutes=1):
            dataset.status = DOWNLOAD_STATUS.IDLE
            dataset.save()
        start_wait_time = time.time()
        while dataset.status == DOWNLOAD_STATUS.DOWNLOADING:
            time.sleep(0.1)
            if time.time() - start_wait_time > 10:
                error_msg = "Dataset is currently being downloaded. Come back later."
                raise TimeoutError(error_msg)

        if squash:
            dataset.delete()
            self.download(verbose=verbose)
        else:
            if dataset.start_date is None or dataset.end_date is None:
                dataset.save()
            if dataset.start_date is None or dataset.end_date is None:
                self.fill_dataset(start_date=start_date, end_date=end_date, dataset=dataset, verbose=verbose)
            else:
                if start_date < dataset.start_date:
                    end = end_date
                    end_date = dataset.start_date - timedelta(milliseconds=interval_to_milliseconds(dataset.controller.interval))
                    self.fill_dataset(start_date=start_date, end_date=end_date, dataset=dataset, verbose=verbose)
                    end_date = end
                if end_date > dataset.end_date:
                    start = start_date
                    start_date = dataset.end_date
                    self.fill_dataset(start_date=start_date, end_date=end_date, dataset=dataset, verbose=verbose)
                    start_date = start
        if verbose > 1:
            print(f"### Finished downloading at {datetime.now(tz=UTC)} (took {datetime.now(tz=UTC) - start_time} seconds)")
        dataset.save()
        return dataset

    def submit_order(
        self,
        controller,
        aggregated_order: dict,
        testing: bool,
    ) -> tuple[dict, dict, dict]:
        receipt = {}
        receipt[SIDES.BUY], executed_amounts_buy, fees_buy = self.send_order_to_exchange(
            side=SIDES.BUY,
            amount=aggregated_order["buy_amount"],
            controller=controller,
            min_trade=aggregated_order["min_trade"],
            price=aggregated_order["price"],
            testing=testing,
        )
        receipt[SIDES.SELL], executed_amounts_sell, feel_sell = self.send_order_to_exchange(
            side=SIDES.SELL,
            amount=aggregated_order["sell_amount"],
            controller=controller,
            min_trade=aggregated_order["min_trade"],
            price=aggregated_order["price"],
            testing=testing,
        )
        return receipt, executed_amounts_buy, executed_amounts_sell, fees_buy, feel_sell

    def send_order_to_exchange(
        self,
        controller,
        side: str,
        amount: float,
        min_trade: float,
        testing: bool,
        price: float,
    ) -> tuple[dict, dict]:
        if amount == 0:
            return {"error": "Amount too low"}, {}, {}

        executed_amounts = {}
        fees = {}
        if testing:
            if side == SIDES.BUY:
                amount /= price
                amount = round_down(amount, controller.lot_size)
                if amount > min_trade:
                    receipt = self.test_order(amount, SIDES.BUY, price, quote=controller.quote, base=controller.base)
                    exec_quote = -float(receipt["cummulativeQuoteQty"])
                    exec_base = 0
                    for elem in receipt["fills"]:
                        exec_base += float(elem["qty"]) - float(elem["commission"])
                        fees[elem["commissionAsset"]] = fees.get(elem["commissionAsset"], 0) + float(elem["commission"])
                    executed_amounts[controller.quote] = exec_quote
                    executed_amounts[controller.base] = exec_base

                else:
                    receipt = {"error": "Amount too low"}

            elif side == SIDES.SELL:
                amount = round_down(amount, controller.lot_size)
                if amount > min_trade:
                    receipt = self.test_order(amount, SIDES.SELL, price, quote=controller.quote, base=controller.base)
                    exec_quote = float(receipt["cummulativeQuoteQty"])
                    exec_base = -float(receipt["origQty"])
                    for elem in receipt["fills"]:
                        exec_quote -= float(elem["commission"])
                        fees[elem["commissionAsset"]] = fees.get(elem["commissionAsset"], 0) + float(elem["commission"])
                    executed_amounts[controller.quote] = exec_quote
                    executed_amounts[controller.base] = exec_base
                else:
                    receipt = {"error": "Amount too low"}

        else:
            # TODO: implement real orders
            error_msg = "IRL orders are not implemented yet. (failsafe to prevent accidental irl orders)."
            raise NotImplementedError(error_msg)
        return receipt, executed_amounts, fees

    def current_free_assets(self) -> dict:
        assets = self.get_info()["balances"]
        current = {}
        for elem in assets:
            if float(elem["free"]) > 0:
                current[elem.get("asset")] = float(elem.get("free"))
        return current

    @staticmethod
    def test_order(amount: float, side: str, price: float, base: str, quote: str) -> dict:
        if side not in (SIDES.BUY, SIDES.SELL):
            error_msg = f"Side must be BUY or SELL. Got {side}"
            raise ValueError(error_msg)

        pair = base + quote
        side_buy = side == SIDES.BUY

        executed_qty = amount
        cummulative_quote_qty = amount * price
        commission = executed_qty * DEFAULT_TAX["BINANCE"] / 100 if side_buy else cummulative_quote_qty * DEFAULT_TAX["BINANCE"] / 100

        commission_asset = base if side_buy else quote
        return {
            "symbol": pair,
            "orderId": None,
            "orderListId": None,
            "clientOrderId": None,
            "transactTime": None,
            "price": price,
            "origQty": amount,
            "executedQty": executed_qty,
            "cummulativeQuoteQty": cummulative_quote_qty,
            "status": "FILLED",
            "timeInForce": "GTC",
            "type": "MARKET",
            "side": side,
            "fills": [
                {
                    "price": price,
                    "qty": amount,
                    "commission": commission,
                    "commissionAsset": commission_asset,
                    "tradeId": None,
                },
            ],
        }

    def executed_amounts(self, receipt: dict, current_free_assets_dict: dict, controller, testing: bool) -> dict:
        executed = {}
        commission = 0
        if receipt == {} or receipt is None:
            return {}
        if testing:
            for fill in receipt.get("fills"):
                commission += float(fill.get("commission"))
            if receipt.get("side") == SIDES.BUY:
                base = receipt.get("fills")[0].get("commissionAsset")
                quote = receipt.get("symbol").replace(base, "")
                executed[base] = float(receipt.get("executedQty")) * (1 - DEFAULT_TAX["BINANCE"] / 100)
                executed[quote] = -float(receipt.get("cummulativeQuoteQty"))
            elif receipt.get("side") == SIDES.SELL:
                quote = receipt.get("fills")[0].get("commissionAsset")
                base = receipt.get("symbol").replace(quote, "")
                executed[base] = -float(receipt.get("executedQty"))
                executed[quote] = float(receipt.get("cummulativeQuoteQty")) * (1 - DEFAULT_TAX["BINANCE"] / 100)
        else:
            while self.current_free_assets(controller) == current_free_assets_dict:
                print("Waiting for order to be executed...")
                sleep(0.01)
            new_free_assets = self.current_free_assets(controller)
            for asset, amount in new_free_assets.items():
                if amount != current_free_assets_dict.get(asset):
                    executed[asset] = amount - current_free_assets_dict.get(asset)
        return executed
