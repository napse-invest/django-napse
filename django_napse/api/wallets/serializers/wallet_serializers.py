from django.db.models import Q
from rest_framework import serializers

from django_napse.api.transactions.serializers import CreditSerializer, DebitSerializer, TransactionSerializer
from django_napse.api.wallets.serializers.currency_serializer import CurrencySerializer
from django_napse.core.models import Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    currencies = CurrencySerializer(many=True, read_only=True)
    value = serializers.SerializerMethodField(read_only=True)
    operations = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Wallet
        fields = [
            "title",
            "value",
            "created_at",
            "currencies",
            "operations",
        ]
        read_only_fields = [
            "value",
            "created_at",
            "currencies",
            "operations",
        ]

    def get_value(self, instance) -> float:
        return instance.value_market()

    def get_operations(self, instance) -> dict:
        transactions = Transaction.objects.filter(Q(from_wallet=instance) | Q(to_wallet=instance)).order_by("created_at")
        transactions_data = TransactionSerializer(transactions, many=True).data
        credits_data = CreditSerializer(instance.credits.all().order_by("created_at"), many=True).data
        debits_data = DebitSerializer(instance.debits.all().order_by("created_at"), many=True).data

        # return {
        #     "credits": CreditSerializer(instance.credits.all().order_by("created_at"), many=True).data,
        #     "debits": DebitSerializer(instance.debits.all().order_by("created_at"), many=True).data,
        #     "transactions": TransactionSerializer(transactions, many=True).data,
        # }
        return credits_data + debits_data + transactions_data
