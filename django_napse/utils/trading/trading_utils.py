from time import sleep

from django_napse.core.models.bots.controller import Controller
from django_napse.utils.constants import DEFAULT_TAX
from django_napse.utils.trading.binance_controller import BinanceController
from django_napse.utils.usefull_functions import round_down


class BinanceExchangeTools:
    """Class used to interact with Binance."""

    def submit_order(
        self,
        order,
        min_trade,
        exchange_controller,
        controller,
        receipt,
        executed_amounts_buy,
        executed_amounts_sell,
    ) -> tuple[dict, dict, dict]:
        """Send the order to the binance exchange.

        Args:
        ----
        order (Order): The Order to send.
        min_trade (float): The minimum amount binance will accept for this pair.
        exchange_controller (BinanceController): Either the NAPSE Binance account controller or the user's controller.
        controller (Controller): The controller of the pair.
        receipt (dict): Normally an empty dict. Used to store the receipt of the order.
        executed_amounts_buy (dict): Normally an empty dict. Used to store the executed amounts of the buy order.
        executed_amounts_sell (dict): Normally an empty dict. Used to store the executed amounts of the sell order.

        Returns:
        -------
        receipt (dict): The receipt of the order.
        executed_amounts_buy (dict): The executed amounts of the buy order.
        executed_amounts_sell (dict): The executed amounts of the sell order.

        Steps:
        -----
        1. Send the buy component of the order.
        2. Send the sell component of the order.
        """
        wallet = order.wallet if order.pk else None
        receipt["BUY"], executed_amounts_buy = self.send_order_to_exchange(
            side="BUY",
            amount=order.buy_amount,
            controller=controller,
            min_trade=min_trade,
            wallet=wallet,
            price=order.price,
        )
        receipt["SELL"], executed_amounts_sell = self.send_order_to_exchange(
            side="SELL",
            amount=order.sell_amount,
            controller=controller,
            min_trade=min_trade,
            wallet=wallet,
            price=order.price,
        )
        return receipt, executed_amounts_buy, executed_amounts_sell

    def send_order_to_exchange(
        self,
        side,
        price,
        amount,
        controller,
        min_trade,
        wallet=None,
    ) -> tuple[dict, dict]:
        """Place an order on the exchange.

        Args:
        ----
        side (str): BUY or SELL
        price (float): The price to buy or sell at (only used in testing environments).
        amount (float): The amount to buy or sell.
        controller (Controller): The controller of the pair.
        min_trade (float): The minimum amount binance will accept for this pair.
        wallet (Wallet, optional): The wallet to use for the order. Defaults to None.

        Returns:
        -------
        receipt: The receipt of the order (given by binance, or calculated by us).
        executed_amounts: The executed amounts of the order (how much the balance of the account has changed).

        Raises:
        ------
        NotImplementedError: Real orders are not implemented yet.
        """
        executed_amounts = {}
        testing = wallet.testing if wallet else True
        amount = round_down(amount, controller.lot_size)
        if testing:
            if side == "BUY":
                if amount > min_trade:
                    receipt = self.test_order(amount, "BUY", price, quote=controller.quote, base=controller.base)
                    exec_quote = -float(receipt["cummulativeQuoteQty"])
                    exec_base = 0
                    for elem in receipt["fills"]:
                        exec_base += float(elem["qty"]) - float(elem["commission"])

                    executed_amounts[controller.quote] = exec_quote
                    executed_amounts[controller.base] = exec_base
                else:
                    receipt = {"error": "Amount too low"}
                    executed_amounts = {}

            elif side == "SELL":
                if amount > min_trade:
                    receipt = self.test_order(amount, "SELL", price, quote=controller.quote, base=controller.base)
                    exec_quote = float(receipt["cummulativeQuoteQty"])
                    exec_base = -float(receipt["origQty"])
                    for elem in receipt["fills"]:
                        exec_quote -= float(elem["commission"])
                    executed_amounts[controller.quote] = exec_quote
                    executed_amounts[controller.base] = exec_base
                else:
                    receipt = {"error": "Amount too low"}
                    executed_amounts = {}
        else:
            # TODO: implement real orders and public exchange GIL
            error_msg = "IRL orders are not implemented yet. (failsafe to prevent accidental irl orders)."
            raise NotImplementedError(error_msg)

        if wallet:
            for ticker, amount in executed_amounts.items():
                if amount < 0:
                    wallet.spend(-amount, ticker)
                else:
                    wallet.top_up(amount, ticker)
        return receipt, executed_amounts

    def swap(self, wallet, amount, from_ticker, to_ticker, pair, price=None):
        """Swap from one asset to another.

        amount is always the amount of the from_ticker asset, in the from_ticker currency.

        Args:
        ----
        wallet (Wallet): The wallet to use for the swap.
        amount (float): How much of the from_ticker asset to swap.
        from_ticker (str): The ticker of the asset to swap from.
        to_ticker (str): The ticker of the asset to swap to.
        pair (str): The pair to use for the swap.
        price (float, optional): Only used for testing. Defaults to None.

        Raises:
        ------
        ValueError: If price is not specified in testing mode.
        ValueError: If pair is not valid for from_ticker and to_ticker.

        Returns:
        -------
        receipt (dict): The receipt of the swap.
        executed_amounts (dict): A dictionnary that summarises the changes of your wallet.
        """
        testing = wallet.testing
        if testing and price is None:
            error_msg = "Price must be specified in testing mode."
            raise ValueError(error_msg)
        if from_ticker + to_ticker == pair:
            side = "SELL"
            base = from_ticker
            quote = to_ticker
        elif to_ticker + from_ticker == pair:
            side = "BUY"
            base = to_ticker
            quote = from_ticker
            if not testing:
                price = Controller.get_asset_price(base, quote)
            amount /= price
        else:
            error_msg = f"Pair {pair} is not valid for {from_ticker} and {to_ticker}"
            raise ValueError(error_msg)

        controller = Controller.get(base=base, quote=quote, exchange="BINANCE", interval="1m")
        receipt = {}
        executed_amounts = {}

        min_trade = controller.min_trade
        receipt, executed_amounts = self.send_order_to_exchange(
            side=side,
            price=price,
            amount=amount,
            controller=controller,
            min_trade=min_trade,
            wallet=wallet,
        )
        return receipt, executed_amounts

    @staticmethod
    def current_free_assets(controller: BinanceController) -> dict:
        """Get the current free assets of the account.

        Args:
        ----
        controller (BinanceController): Used to communicate with Binance

        Returns:
        -------
        dict: Free assets. Shape: {"asset": amount}
        """
        assets = controller.get_info()["balances"]
        current = {}
        for elem in assets:
            if float(elem["free"]) > 0:
                current[elem.get("asset")] = float(elem.get("free"))
        return current

    @staticmethod
    def test_order(amount: float, side: str, price: float, base: str, quote: str) -> dict:
        """Create a fictional receipt for a test order.

        Args:
        ----
        amount (float): amount to buy or sell
        side (str): BUY or SELL
        price (float): current price
        base (str): base ticker
        quote (str): quote ticker

        Raises:
        ------
        ValueError: If side is not BUY or SELL

        Returns:
        -------
        dict: The fake receipt.
        """
        if side not in ("BUY", "SELL"):
            error_msg = f"Side must be BUY or SELL. Got {side}"
            raise ValueError(error_msg)

        pair = base + quote
        side_buy = side == "BUY"

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
        """Calculate the difference between the current free assets and the free assets before the order.

        Returns the executed amounts of said order.

        Args:
        ----
        receipt (dict): The receipt of the order.
        current_free_assets_dict (dict): The free assets before the order.
        controller (BinanceController): Used to communicate with Binance
        testing (bool): If the order is a test order.

        Returns:
        -------
        dict: The executed amounts. Shape: {"asset": amount}
        """
        executed = {}
        commission = 0
        if receipt == {} or receipt is None:
            return {}
        if testing:
            for fill in receipt.get("fills"):
                commission += float(fill.get("commission"))
            if receipt.get("side") == "BUY":
                base = receipt.get("fills")[0].get("commissionAsset")
                quote = receipt.get("symbol").replace(base, "")
                executed[base] = float(receipt.get("executedQty")) * (1 - DEFAULT_TAX["BINANCE"] / 100)
                executed[quote] = -float(receipt.get("cummulativeQuoteQty"))
            elif receipt.get("side") == "SELL":
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


EXCHANGE_TOOLS = {
    "BINANCE": BinanceExchangeTools,
}
