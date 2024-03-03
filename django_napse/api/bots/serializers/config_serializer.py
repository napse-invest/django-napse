from django_napse.core.models.bots.config import BotConfig
from django_napse.utils.serializers import BoolField, Serializer, UUIDField


class ConfigSerializer(Serializer):
    """Serialize a BotConfig instance."""

    Model = BotConfig
    read_only = True

    uuid = UUIDField()
    space = UUIDField(source="space.uuid")
    immutable = BoolField()
