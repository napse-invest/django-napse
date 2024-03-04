from rest_framework import serializers

from django_napse.api.bots.serializers import BotSerializer
from django_napse.core.models import Bot, Cluster
from django_napse.utils.serializers import BoolField, FloatField, Serializer, UUIDField


class ClusterSerializer(Serializer):
    """Serializer for Cluster model."""

    Model = Cluster

    template_bot = BotSerializer()
    share = FloatField()
    breakpoint = FloatField()
    autoscale = BoolField()


class ClusterFormatterSerializer(serializers.Serializer):
    """Format cluster dictionnary for fleet creation."""

    template_bot = UUIDField(required=True)
    share = FloatField(required=True)
    breakpoint = FloatField(required=True)
    autoscale = BoolField(required=True)

    def validate(self, data: dict[str, any]) -> dict[str, any]:
        """Validate data & return it for fleet creation."""
        data = super().validate(data)
        try:
            bot = Bot.objects.get(uuid=data.pop("template_bot"))
        except Bot.DoesNotExist:
            error_msg: str = "Template bot does not exist."
            raise serializers.ValidationError(error_msg) from None
        data["template_bot"] = bot
        return data
