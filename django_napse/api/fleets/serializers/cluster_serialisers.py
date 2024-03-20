from typing import ClassVar

from rest_framework import serializers

from django_napse.api.bots.serializers import BotSerializer
from django_napse.core.models import Bot, Cluster


class ClusterSerializerV1(serializers.ModelSerializer):
    """Serializer for Cluster model."""

    template_bot = BotSerializer()

    class Meta:  # noqa: D106
        model = Cluster
        fields: ClassVar[list[str]] = [
            "template_bot",
            "share",
            "breakpoint",
            "autoscale",
        ]


class ClusterFormatterSerializer(serializers.Serializer):
    """Format cluster dictionnary for fleet creation."""

    template_bot = serializers.UUIDField(required=True)
    share = serializers.FloatField(required=True)
    breakpoint = serializers.IntegerField(required=True)
    autoscale = serializers.BooleanField(required=True)

    def validate(self, data: dict[str, any]) -> dict[str, any]:
        """Validate the data & get template bot instance."""
        data = super().validate(data)
        try:
            bot = Bot.objects.get(uuid=data.pop("template_bot"))
        except Bot.DoesNotExist:
            error_msg: str = "Template bot does not exist."
            raise serializers.ValidationError(error_msg) from None
        data["template_bot"] = bot
        return data
