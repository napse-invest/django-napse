from rest_framework import serializers

from django_napse.api.bots.serializers.strategy_serializer import StrategySerializer
from django_napse.core.models import Bot


class BotSerializer(serializers.ModelSerializer):
    strategy = StrategySerializer()

    class Meta:
        model = Bot
        fields = [
            "name",
            "uuid",
            "strategy",
        ]
        read_only_fields = fields
