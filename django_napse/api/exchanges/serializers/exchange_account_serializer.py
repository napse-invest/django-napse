from django_napse.core.models import ExchangeAccount
from django_napse.utils.serializers import BoolField, Serializer, StrField, UUIDField


class ExchangeAccountSerializer(Serializer):
    """Serializer for ExchangeAccount."""

    Model = ExchangeAccount

    uuid = UUIDField()
    exchange = StrField(source="exchange.name", required=True)
    name = StrField(required=True)
    description = StrField(required=True)
    testing = BoolField(required=True)
