from rest_framework import serializers

from django_napse.core.models.bots.config import BotConfig


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotConfig
        fields = "__all__"
        read_only_fields = [
            "uuid",
            "immutable",
        ]
