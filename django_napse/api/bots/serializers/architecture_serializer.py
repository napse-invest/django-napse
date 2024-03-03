from django_napse.core.models.bots.architecture import Architecture
from django_napse.utils.serializers import IntField, Serializer


class ArchitectureSerializer(Serializer):
    """Serialize an Architecture instance."""

    Model = Architecture
    read_only = True

    id = IntField()
