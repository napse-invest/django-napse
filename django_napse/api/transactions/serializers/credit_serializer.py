from rest_framework import serializers

from django_napse.core.models import credit


class CreditSerializer(serializers.ModelSerializer):
    operation_type = serializers.CharField(default="CREDIT")

    class Meta:
        model = credit
        fields = [
            "amount",
            "ticker",
            "operation_type",
            "created_at",
        ]
        read_only_fields = fields
