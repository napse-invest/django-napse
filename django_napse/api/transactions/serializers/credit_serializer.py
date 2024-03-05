from django_napse.core.models import Credit
from django_napse.utils.serializers import DatetimeField, FloatField, Serializer, StrField


class CreditSerializer(Serializer):
    """Serializer for Credit instance."""

    Model = Credit
    read_only = True

    amount = FloatField()
    ticker = StrField()
    operation_type = StrField(default="CREDIT")
    created_at = DatetimeField()
