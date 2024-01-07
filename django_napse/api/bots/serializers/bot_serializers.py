from rest_framework import serializers

from django_napse.api.bots.serializers.strategy_serializer import StrategySerializer
from django_napse.core.models import Bot, BotHistory


class BotSerializer(serializers.ModelSerializer):
    strategy = StrategySerializer()
    delta = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bot
        fields = [
            "name",
            "uuid",
            "strategy",
            "value",
            "delta",
        ]
        read_only_fields = [
            "uuid",
            "value",
            "delta",
        ]

    def get_delta(self, instance) -> float:
        """Delta on the last 30 days."""
        try:
            history = BotHistory.objects.get(owner=instance)
        except BotHistory.DoesNotExist:
            return 0
        return history.get_delta()
