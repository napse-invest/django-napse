from rest_framework import serializers

from django_napse.api.bots.serializers import BotSerializer
from django_napse.core.models import Bot, Cluster, Strategy


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

    bot_strategy = serializers.UUIDField(required=True)
    bot_name = serializers.CharField(required=True)
    share = serializers.FloatField(required=True)
    breakpoint = serializers.IntegerField(required=True)
    autoscale = serializers.BooleanField(required=True)

    def validate(self, data):
        data = super().validate(data)
        try:
            strategy = Strategy.objects.get(uuid=data["bot_strategy"])
        except Strategy.DoesNotExist:
            error_msg: str = "Strategy does not exist"
            raise serializers.ValidationError(error_msg) from None
        else:
            data["bot_strategy"] = strategy
        return data

    def create(self, validated_data):
        """Return cluster dict for fleet creation."""
        template_bot = Bot.objects.create(
            name=validated_data.pop("bot_name"),
            strategy=validated_data.pop("bot_strategy"),
        )
        return {"template_bot": template_bot, **validated_data}
