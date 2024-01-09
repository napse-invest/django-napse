from rest_framework import serializers

from django_napse.api.bots.serializers import BotSerializer
from django_napse.core.models import Bot, Cluster


class ClusterSerializerV1(serializers.ModelSerializer):
    template_bot = BotSerializer()

    class Meta:
        model = Cluster
        fields = [
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

    def validate(self, data):
        data = super().validate(data)
        try:
            bot = Bot.objects.get(uuid=data.pop("template_bot"))
        except Bot.DoesNotExist:
            error_msg: str = "Template bot does not exist."
            raise serializers.ValidationError(error_msg) from None
        data["template_bot"] = bot
        return data

    def create(self, validated_data):
        return super().create(validated_data)
