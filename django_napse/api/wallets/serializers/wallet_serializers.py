from __future__ import annotations

from typing import ClassVar

from django.db.models import Q
from rest_framework import serializers

from django_napse.api.histories.serializers.history import HistorySerializer
from django_napse.api.transactions.serializers import CreditSerializer, DebitSerializer, TransactionSerializer
from django_napse.api.wallets.serializers.currency_serializer import CurrencySerializer
from django_napse.core.models import Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    """Serialize a wallet instance."""

    currencies = CurrencySerializer(many=True, read_only=True)
    value = serializers.SerializerMethodField(read_only=True)
    operations = serializers.SerializerMethodField(read_only=True)
    history = HistorySerializer(many=False, read_only=True)

    class Meta:  # noqa: D106
        model = Wallet
        fields: ClassVar[list[str]] = [
            "title",
            "value",
            "created_at",
            "currencies",
            "operations",
            "history",
        ]
        read_only_fields: ClassVar[list[str]] = [
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
        return credits_data + debits_data + transactions_data
