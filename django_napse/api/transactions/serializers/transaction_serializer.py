from rest_framework import serializers

from django_napse.core.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    operation_type = serializers.CharField(default="TRANSACTION")

    class Meta:
        model = Transaction
        fields = [
            "amount",
            "ticker",
            "operation_type",
            "created_at",
        ]
        read_only_fields = fields
