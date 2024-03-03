from django_napse.core.models import Transaction
from django_napse.utils.serializers import DatetimeField, FloatField, Serializer, StrField


class TransactionSerializer(Serializer):
    """Serialize a transaction instance."""

    Model = Transaction
    read_only = True

    amount = FloatField()
    ticker = StrField()
    operation_type = StrField(default="TRANSACTION")
    created_at = DatetimeField()
