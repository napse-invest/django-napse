from rest_framework import serializers

from django_napse.api.bots.serializers.strategy_serializer import StrategySerializer
from django_napse.core.models.bots.plugin import Plugin


class PluginSerializer(serializers.ModelSerializer):
    strategy = StrategySerializer()

    class Meta:
        model = Plugin
        fields = "__all__"
        read_only_fields = [
            "id",
        ]
