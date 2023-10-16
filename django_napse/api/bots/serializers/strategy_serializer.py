from rest_framework import serializers

from django_napse.api.bots.serializers.architecture_serializer import ArchitectureSerializer
from django_napse.api.bots.serializers.config_serializer import ConfigSerializer
from django_napse.core.models.bots.strategy import Strategy


class StrategySerializer(serializers.ModelSerializer):
    config = ConfigSerializer()
    architecture = ArchitectureSerializer()

    class Meta:
        model = Strategy
        fields = "__all__"
