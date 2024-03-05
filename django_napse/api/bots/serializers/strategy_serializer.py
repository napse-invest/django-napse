from django_napse.api.bots.serializers.architecture_serializer import ArchitectureSerializer
from django_napse.api.bots.serializers.config_serializer import ConfigSerializer
from django_napse.core.models.bots.strategy import Strategy
from django_napse.utils.serializers import Serializer


class StrategySerializer(Serializer):
    """Serialize a Strategy instance."""

    Model = Strategy
    read_only = True

    config = ConfigSerializer()
    architecture = ArchitectureSerializer()
