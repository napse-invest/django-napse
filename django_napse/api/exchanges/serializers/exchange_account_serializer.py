from rest_framework import serializers

from django_napse.api.spaces.serializers import SpaceSerializer
from django_napse.core.models import ExchangeAccount


class ExchangeAccountSerializer(serializers.ModelSerializer):
    exchange = serializers.CharField(source="exchange.name")

    class Meta:
        model = ExchangeAccount
        fields = [
            "uuid",
            "exchange",
            "name",
            "testing",
        ]
        read_only_fields = [
            "uuid",
            "exchange",
            "testing",
        ]


class ExchangeAccountDetailSerializer(serializers.ModelSerializer):
    exchange = serializers.CharField(source="exchange.name")
    spaces = SpaceSerializer(many=True, read_only=True)

    class Meta:
        model = ExchangeAccount
        fields = [
            "uuid",
            "exchange",
            "name",
            "testing",
            "description",
            "created_at",
            "spaces",
        ]
        read_only_fields = [
            "uuid",
            "exchange",
            "testing",
            "created_at",
            "spaces",
        ]
