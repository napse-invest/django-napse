from rest_framework import serializers

from django_napse.api.bots.serializers.strategy_serializer import StrategySerializer
from django_napse.core.models import Bot


class BotSerializer(serializers.ModelSerializer):
    StrategySerializer = StrategySerializer()

    class Meta:
        model = Bot
        fields = [
            "name",
            "uuid",
        ]
        read_only_fields = fields
