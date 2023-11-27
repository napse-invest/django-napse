from rest_framework import serializers

from django_napse.core.models import Currency
from django_napse.core.models.bots.controller import Controller


class CurrencySerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Currency
        fields = [
            "mbp",
            "ticker",
            "amount",
            "value",
        ]
        read_only_fields = fields

    def get_value(self, instance):
        return instance.amount * Controller.get_asset_price(
            exchange_account=instance.wallet.exchange_account,
            base=instance.ticker,
        )
