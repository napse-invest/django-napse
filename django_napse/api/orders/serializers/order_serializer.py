from typing import ClassVar

from rest_framework import serializers

from django_napse.core.models import Order
from django_napse.utils.constants import SIDES


class OrderSerializer(serializers.ModelSerializer):
    """.

    {
        "side": "BUY",
        "completed": true,
        "spent": {
            "ticker": "BTC",
            "amount": 0.1,
            "price": 1,
            "value": 0.1,
        },
        "received": {
            "ticker": "MATIC",
            "amount": 995,
            "price": 0.0001,
            "value": 0.095,
        },
        "fees": {
            "ticker": "BTC",
            "amount": 5,
            "price": 0.0001,
            "value": 0.05,
        },
        "created_at": "2021-09-01T12:00:00Z",
    }
    """

    spent = serializers.SerializerMethodField()
    received = serializers.SerializerMethodField()
    fees = serializers.SerializerMethodField()

    class Meta:  # noqa: D106
        model = Order
        fields: ClassVar[list[str]] = [
            "side",
            "completed",
            "spent",
            "received",
            "fees",
            "created_at",
        ]
        read_only_fields = fields

    def get_spent(self, instance: Order) -> dict[str, str | float]:
        """Return spend informations."""
        exit_amount = instance.exit_amount_quote if instance.side == SIDES.BUY else instance.exit_amount_base
        amount = instance.debited_amount - exit_amount
        ticker = instance.tickers_info().get("spent_ticker")
        return {
            "ticker": ticker,
            "amount": amount,
            "price": 1,
            "value": amount,
        }

    def get_received(self, instance: Order) -> dict[str, str | float]:
        """Return receive informations."""
        amount = instance.exit_amount_base if instance.side == SIDES.BUY else instance.exit_amount_quote
        ticker = instance.tickers_info().get("received_ticker")
        price = instance.price
        return {
            "ticker": ticker,
            "amount": amount,
            "price": price,
            "value": amount * price,
        }

    def get_fees(self, instance: Order) -> dict[str, str | float]:
        """Return fees info about the market order."""
        return {
            "ticker": instance.fee_ticker,
            "amount": instance.fees,
            "value": instance.fees * instance.price,
        }
