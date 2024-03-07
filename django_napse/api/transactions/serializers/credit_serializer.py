from typing import ClassVar

from rest_framework import serializers

from django_napse.core.models import Credit


class CreditSerializer(serializers.ModelSerializer):
    """Serializer for Credit instance."""

    operation_type = serializers.CharField(default="CREDIT")

    class Meta:  # noqa: D106
        model = Credit
        fields: ClassVar[list[str]] = [
            "amount",
            "ticker",
            "operation_type",
            "created_at",
        ]
        read_only_fields = fields
