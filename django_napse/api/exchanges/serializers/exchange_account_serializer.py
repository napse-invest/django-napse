from django_napse.core.models import ExchangeAccount
from rest_framework import serializers


class ExchangeAccountSerializer(serializers.ModelSerializer):
    exchange_name = serializers.CharField(source="exchange.name")

    class Meta:
        model = ExchangeAccount
        fields = ["exchange_name", "name", "testing", "description", "created_at"]
        read_only_fields = ["exchange_name", "testing", "created_at"]
