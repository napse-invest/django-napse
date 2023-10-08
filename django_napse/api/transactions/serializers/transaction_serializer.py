from rest_framework import serializers

from django_napse.core.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "amount",
            "ticker",
            "transaction_type",
            "created_at",
        ]
        read_only_fields = fields
