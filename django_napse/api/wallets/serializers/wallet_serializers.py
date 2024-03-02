from __future__ import annotations

from django.db.models import Q

from django_napse.api.transactions.serializers import CreditSerializer, DebitSerializer, TransactionSerializer
from django_napse.api.wallets.serializers.currency_serializer import CurrencySerializer
from django_napse.core.models import Transaction, Wallet
from django_napse.utils.serializers import DatetimeField, MethodField, Serializer, StrField


class WalletSerializer(Serializer):
    """Serialize a wallet instance."""

    Model = Wallet
    read_only = True

    title = StrField()
    value = MethodField()
    currencies = CurrencySerializer(many=True)
    operations = MethodField()
    created_at = DatetimeField()

    def get_value(self, instance: Wallet) -> float:
        """Return market value of the wallet."""
        return instance.value_market()

    def get_operations(self, instance: Wallet) -> dict:
        """Return all operations of the wallet."""
        transactions = Transaction.objects.filter(Q(from_wallet=instance) | Q(to_wallet=instance)).order_by("created_at")
        transactions_data = TransactionSerializer(transactions, many=True).data
        credits_data = CreditSerializer(instance.credits.all().order_by("created_at"), many=True).data
        debits_data = DebitSerializer(instance.debits.all().order_by("created_at"), many=True).data

        return credits_data + debits_data + transactions_data
