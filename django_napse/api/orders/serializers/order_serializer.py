from rest_framework import serializers

from django_napse.core.models import Order
from django_napse.core.models.bots.controller import Controller
from django_napse.utils.constants import SIDES


class OrderSerializer(serializers.ModelSerializer):
    """.

    {
        "side": "BUY",
        "completed": true,
        "spent": {
            "ticker": "BTC",
            "amount": 0.1,
            "price": 10000,
            "value": 1000,
        },
        "received": {
            "ticker": "USDT",
            "amount": 1000,
            "price": 1,
            "value": 1000,
        },
        "fees": {
            "ticker": "BTC",
            "amount": 0.01,
            "price": 10000,
            "value": 100,
        },
        "created_at": "2021-09-01T12:00:00Z",
    }
    """

    spent = serializers.SerializerMethodField()
    received = serializers.SerializerMethodField()
    fees = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "side",
            "completed",
            "spent",
            "received",
            "fees",
            "created_at",
        ]
        read_only_fields = fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exchange_account = self.instance.connection.space.exchange_account

    def get_spent(self, instance):
        """Return spend informations."""
        exit_amount = instance.exit_amount_quote if instance.side == SIDES.BUY else instance.exit_amount_base
        amount = instance.debited_amount - exit_amount
        ticker = instance.tickers_info().get("spent_ticker")
        price = Controller.get_asset_price(exchange_account=self.exchange_account, base=ticker)
        return {
            "ticker": ticker,
            "amount": amount,
            "price": price,
            "value": amount * price,
        }

    def get_receive(self, instance):
        """Rerturn receive informations."""
        amount = instance.exit_amount_base if instance.side == SIDES.BUY else instance.exit_amount_quote
        ticker = instance.tickers_info().get("received_ticker")
        price = Controller.get_asset_price(exchange_account=self.exchange_account, base=ticker)
        return {
            "ticker": ticker,
            "amount": amount,
            "price": price,
            "value": amount * price,
        }

    def get_fees(self, instance):
        return {
            "ticker": instance.fee_ticker,
            "amount": instance.fees,
            "value": instance.fees * instance.price,
        }

    def save(self, **kwargs):
        error_msg: str = "It's impossible to create ormodify an order."
        raise serializers.ValidationError(error_msg)
