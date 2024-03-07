from typing import ClassVar

from rest_framework import serializers

from django_napse.core.models.bots.config import BotConfig


class ConfigSerializer(serializers.ModelSerializer):
    """Serialize a BotConfig instance."""

    class Meta:  # noqa: D106
        model = BotConfig
        fields = "__all__"
        read_only_fields: ClassVar[list[str]] = [
            "uuid",
            "immutable",
        ]
