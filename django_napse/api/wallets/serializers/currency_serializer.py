from rest_framework import serializers

from django_napse.core.models import Currency


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = [
            "mbp",
            "ticker",
            "amount",
        ]
        read_only_fields = fields
