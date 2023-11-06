from rest_framework import serializers

from django_napse.core.models import ExchangeAccount


class ExchangeAccountSerializer(serializers.ModelSerializer):
    exchange = serializers.CharField(source="exchange.name")

    class Meta:
        model = ExchangeAccount
        fields = [
            "uuid",
            "exchange",
            "name",
            "description",
            "testing",
        ]
        read_only_fields = [
            "uuid",
            "exchange",
            "testing",
        ]
