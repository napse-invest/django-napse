from django_napse.core.models import Debit
from django_napse.utils.serializers import DatetimeField, FloatField, Serializer, StrField


class DebitSerializer(Serializer):
    """Serializer for Debit instance."""

    Model = Debit
    read_only = True

    amount = FloatField()
    ticker = StrField()
    operation_type = StrField(default="DEBIT")
    created_at = DatetimeField()
