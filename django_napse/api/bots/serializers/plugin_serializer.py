from django_napse.api.bots.serializers.strategy_serializer import StrategySerializer
from django_napse.core.models.bots.plugin import Plugin
from django_napse.utils.serializers import Serializer, StrField


class PluginSerializer(Serializer):
    """Serialize a Plugin instance."""

    Model = Plugin
    read_only = True

    strategy = StrategySerializer()
    category = StrField()
