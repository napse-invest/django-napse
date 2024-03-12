from typing import ClassVar

from rest_framework import serializers

from django_napse.core.models import debit


class DebitSerializer(serializers.ModelSerializer):
    """Serializer for Debit instance."""

    operation_type = serializers.CharField(default="DEBIT")

    class Meta:  # noqa: D106
        model = debit
        fields: ClassVar[list[str]] = [
            "amount",
            "ticker",
            "operation_type",
            "created_at",
        ]
        read_only_fields = fields
