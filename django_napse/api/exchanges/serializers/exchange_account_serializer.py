from typing import ClassVar

from rest_framework import serializers

from django_napse.core.models import ExchangeAccount


class ExchangeAccountSerializer(serializers.ModelSerializer):
    """Serializer for ExchangeAccount."""

    exchange = serializers.CharField(source="exchange.name")

    class Meta:  # noqa: D106
        model = ExchangeAccount
        fields: ClassVar[list[str]] = [
            "uuid",
            "exchange",
            "name",
            "description",
            "testing",
        ]
        read_only_fields: ClassVar[list[str]] = [
            "uuid",
            "exchange",
            "testing",
        ]
