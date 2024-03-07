from typing import ClassVar

from rest_framework import serializers

from django_napse.core.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """Serialize a transaction instance."""

    operation_type = serializers.CharField(default="TRANSACTION")

    class Meta:  # noqa: D106
        model = Transaction
        fields: ClassVar[list[str]] = [
            "amount",
            "ticker",
            "operation_type",
            "created_at",
        ]
        read_only_fields = fields
