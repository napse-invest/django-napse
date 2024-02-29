from django_napse.api.spaces.serializers.space_serializers import SpaceSerializer
from django_napse.core.models import ExchangeAccount
from django_napse.utils.serializers import BoolField, Serializer, StrField, UUIDField


class ExchangeAccountDetailSerializer(Serializer):
    """Serializer for ExchangeAccount detail."""

    Model = ExchangeAccount
    is_read_only_serializer = True

    uuid = UUIDField()
    exchange = StrField(source="exchange.name")
    name = StrField()
    description = StrField()
    testing = BoolField()
    created_at = StrField()
    spaces = SpaceSerializer(many=True, read_only=True)
