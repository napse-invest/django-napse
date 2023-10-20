from rest_framework import serializers

from django_napse.core.models import debit


class DebitSerializer(serializers.ModelSerializer):
    operation_type = serializers.CharField(default="DEBIT")

    class Meta:
        model = debit
        fields = [
            "amount",
            "ticker",
            "operation_type",
            "created_at",
        ]
        read_only_fields = fields
