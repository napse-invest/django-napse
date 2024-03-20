from typing import ClassVar

from rest_framework import serializers

from django_napse.core.models.bots.architecture import Architecture


class ArchitectureSerializer(serializers.ModelSerializer):
    """Serialize an Architecture instance."""

    class Meta:  # noqa: D106
        model = Architecture
        fields = "__all__"
        read_only_fields: ClassVar[list[str]] = [
            "id",
        ]
