from typing import ClassVar

from rest_framework import serializers

from django_napse.api.spaces.serializers.space_serializers import SpaceSerializer
from django_napse.core.models import ExchangeAccount


class ExchangeAccountDetailSerializer(serializers.ModelSerializer):
    """Serializer for ExchangeAccount detail."""

    exchange = serializers.CharField(source="exchange.name")
    spaces = SpaceSerializer(many=True, read_only=True)

    class Meta:  # noqa: D106
        model = ExchangeAccount
        fields: ClassVar[list[str]] = [
            "uuid",
            "exchange",
            "name",
            "testing",
            "description",
            "created_at",
            "spaces",
        ]
        read_only_fields: ClassVar[list[str]] = fields
