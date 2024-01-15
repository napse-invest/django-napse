from rest_framework import serializers

from django_napse.core.models import Order
from django_napse.utils.constants import SIDES


class OrderSerializer(serializers.ModelSerializer):
    ticker = serializers.SerializerMethodField(read_only=True)
    amount_spent = serializers.SerializerMethodField(read_only=True)
    amount_received = serializers.SerializerMethodField(read_only=True)
    fees = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "side",
            "ticker",
            "price",
            "completed",
            "amount_spent",
            "amount_received",
            "fees",
        ]
        read_only_fields = fields

    def get_ticker(self, instance):
        return instance.fee_ticker

    def get_amount_spent(self, instance):
        exit_amount = instance.exit_amount_quote if instance.side == SIDES.BUY else instance.exit_amount_base
        return instance.debited_amount - exit_amount

    def get_amount_received(self, instance):
        return instance.exit_amount_base if instance.side == SIDES.BUY else instance.exit_amount_quote

    def get_fees(self, instance):
        return {
            "ticker": instance.fee_ticker,
            "amount": instance.fees,
            "value": instance.fees * instance.price,
        }

    def save(self, **kwargs):
        error_msg: str = "It's impossible to create ormodify an order."
        raise serializers.ValidationError(error_msg)
