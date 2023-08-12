from django.apps import apps
from django.db import models

from django_napse.utils.constants import EXCHANGE_PAIRS, ORDER_LEEWAY_PERCENTAGE, SIDES, TRANSACTION_TYPES
from django_napse.utils.errors import OrderError


class OrderManager(models.Manager):
    def create(
        self,
        batch,
        connection,
        asked_for_amount: float,
        asked_for_ticker: str,
        pair: str,
        price: float,
        side: str,
    ):
        if side not in [SIDES.BUY, SIDES.SELL, SIDES.KEEP]:
            error_msg = f"Side {side} is not valid."
            raise OrderError.InvalidOrder(error_msg)

        if side == SIDES.BUY and asked_for_ticker != batch.controller.quote:
            error_msg = f"Ticker {asked_for_ticker} is not valid for a buy order. Should be {batch.controller.quote}."
            raise OrderError.InvalidOrder(error_msg)

        if side == SIDES.SELL and asked_for_ticker != batch.controller.base:
            error_msg = f"Ticker {asked_for_ticker} is not valid for a sell order. Should be {batch.controller.base}."
            raise OrderError.InvalidOrder(error_msg)

        # if side == SIDES.KEEP:
        #     return None

        order = self.model(
            batch=batch,
            connection=connection,
            asked_for_amount=asked_for_amount,
            pair=pair,
            price=price,
            side=side,
            asked_for_ticker=asked_for_ticker,
        )
        order.save()

        OrderWallet = apps.get_model("django_napse_core", "OrderWallet")
        wallet = OrderWallet.objects.create(title=f"Wallet for order {order.pk}", owner=order)

        Transaction = apps.get_model("django_napse_core", "Transaction")
        Transaction.objects.create(
            from_wallet=connection.wallet,
            to_wallet=wallet,
            amount=asked_for_amount * (1 + ORDER_LEEWAY_PERCENTAGE / 100),
            ticker=EXCHANGE_PAIRS[connection.space.exchange_account.exchange.name][pair]["base" if side == SIDES.SELL else "quote"],
            transaction_type=TRANSACTION_TYPES.ORDER_DEPOSIT,
        )
        order.debited_amount = asked_for_amount * (1 + ORDER_LEEWAY_PERCENTAGE / 100)
        order.save()
        return order
