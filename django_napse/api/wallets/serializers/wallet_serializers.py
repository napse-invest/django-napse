from django.db.models import Q
from rest_framework import serializers

from django_napse.api.transactions.serializers import CreditSerializer, DebitSerializer, TransactionSerializer
from django_napse.api.wallets.serializers.currency_serializer import CurrencySerializer
from django_napse.core.models import Transaction, Wallet


class WalletDetailSerializer(serializers.ModelSerializer):
    currencies = CurrencySerializer(many=True, read_only=True)
    value = serializers.SerializerMethodField(read_only=True)
    operations = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Wallet
        fields = [
            "title",
            "value",
            "currencies",
            "created_at",
        ]
        read_only_fields = [
            "value",
            "currencies",
            "created_at",
        ]

    def get_value(self, instance) -> float:
        return instance.value_market()

    def get_operations(self, instance) -> dict:
        transactions = Transaction.objects.filter(Q(from_wallet=instance) | Q(to_wallet=instance)).order_by("created_at")
        return {
            "credits": CreditSerializer(instance.credits.all().order_by("created_at"), many=True).data,
            "debits": DebitSerializer(instance.debits.all().order_by("created_at"), many=True).data,
            "transactions": TransactionSerializer(transactions, many=True).data,
        }
