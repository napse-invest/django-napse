#!/usr/bin/env python3
"""Commmunication interface with binance account."""


# Binance
from time import sleep

import binance.enums as binance_enums
from binance.client import Client
from binance.exceptions import BinanceAPIException
from django.apps import apps
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout


class BinanceController:
    """Commmunication interface with binance account."""

    def __init__(self, clef_api, clef_secrete):
        client_created = False
        retries = 0
        while not client_created:
            try:
                self.client = Client(clef_api, clef_secrete)
                client_created = True
            except ConnectTimeout:
                print(f"ConnectionTimout error while creating client (try: {retries}), retrying...")
                sleep(1)
            except ConnectionError:
                print(f"ConnectionError error while creating client (try: {retries}), retrying...")
                sleep(1)
            except ReadTimeout:
                print(f"ReadTimeout error while creating client (try: {retries}), retrying...")
                sleep(1)
            else:
                if retries > 0:
                    print(f"Client created after {retries} retries.")
            retries += 1
        self._nb_retry: int = 3
        self._recv: int = 5000

    def get_info(self) -> dict:
        """Get the data of the binance account."""
        meter = 0
        while meter < self._nb_retry:
            meter += 1
            try:
                return self.client.get_account(recvWindow=self._recv)
            except ReadTimeout:
                continue
            except BinanceAPIException:
                continue

        return {"error": 408}

    def get_balance(self, ticker: str) -> dict:
        """Return balance of the selected ticker."""
        meter = 0
        while meter < self._nb_retry:
            meter += 1
            try:
                return self.client.get_asset_balance(asset=ticker.upper(), recvWindow=self._recv)
            except ReadTimeout:
                continue
            except BinanceAPIException:
                continue
        return {"error": 408}

    def get_trades(self, pair) -> dict:
        """Return trades of the selected pair."""
        meter = 0
        while meter < self._nb_retry:
            meter += 1
            try:
                return self.client.get_my_trades(symbol=pair.upper(), recvWindow=self._recv)
            except ReadTimeout:
                continue
            except BinanceAPIException:
                continue
        return {"error": 408}

    def get_tickers(self) -> list[dict]:
        """Return all available tickers."""
        meter = 0
        while meter < self._nb_retry:
            meter += 1
            try:
                return self.client.get_all_tickers()

            except ConnectionError:
                continue
        return [{"error": 408}]

    def cancel_order(self, pair: str, order_id: str) -> dict:
        """Cancel an order via its id."""
        return self.client.cancel_order(
            symbol=pair.upper(),
            orderId=order_id,
            recvWindow=self._recv,
        )

    def get_all_order(self, pair) -> dict:
        """Return all orders of a selected pair."""
        return self.client.get_all_orders(symbol=pair, recvWindow=self._recv)

    def fetch_all_order(self, pair, limit=10):
        """Fetch all orders of a selected pair."""
        return self.client.get_all_orders(symbol=pair, limit=limit, recvWindow=self._recv)

    def buy_market(self, pair: str, quantity: float) -> dict:
        """Place a spot buy market order.

        !!! WARNING: quantity is in base currency !!!
        """
        Controller = apps.get_model("django_napse_core", "Controller")
        meter = 0
        while meter < self._nb_retry:
            meter += 1

            _, current_candle = Controller.get_candles(pair, "1m")
            price = current_candle["C"]
            quantity = quantity / price
            try:
                order = self.client.order_market_buy(symbol=pair.upper(), quantity=quantity, recvWindow=self._recv)
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
        while meter < self._nb_retry:
            meter += 1

            try:
                order = self.client.order_market_sell(symbol=pair.upper(), quantity=quantity, recvWindow=self._recv)
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
            recvWindow=self._recv,
        )
