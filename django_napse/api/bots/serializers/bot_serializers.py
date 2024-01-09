from rest_framework import serializers
from rest_framework.fields import empty

from django_napse.api.bots.serializers.strategy_serializer import StrategySerializer
from django_napse.core.models import Bot, BotHistory


class BotSerializer(serializers.ModelSerializer):
    strategy = StrategySerializer()
    delta = serializers.SerializerMethodField(read_only=True)
    space = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bot
        fields = [
            "name",
            "uuid",
            "strategy",
            "value",
            "delta",
            "fleet",
            "space",
            "exchange_account",
        ]
        read_only_fields = [
            "uuid",
            "value",
            "delta",
            "fleet",
            "space",
            "exchange_account",
        ]

    def __init__(self, instance=None, data=empty, space=None, **kwargs):
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def get_delta(self, instance) -> float:
        """Delta on the last 30 days."""
        try:
            history = BotHistory.objects.get(owner=instance)
        except BotHistory.DoesNotExist:
            return 0
        return history.get_delta()

    def get_space(self, instance):
        if self.space is None:
            return None
        return self.space.uuid

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["fleet"] = representation["fleet"].uuid
        representation["exchange_account"] = representation["exchange_account"].uuid
        return representation
