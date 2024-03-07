from typing import ClassVar

from rest_framework import serializers

from django_napse.api.permissions.serializers import PermissionSerializer
from django_napse.auth.models import NapseAPIKey


class NapseAPIKeySerializer(serializers.ModelSerializer):
    """Serialize a NapseAPIKey instance."""

    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:  # noqa: D106
        model = NapseAPIKey
        fields: ClassVar[list[str]] = [
            "name",
            "prefix",
            "permissions",
            "is_master_key",
            "revoked",
            "description",
        ]


class NapseAPIKeySpaceSerializer(serializers.ModelSerializer):
    """Serialize a NapseAPIKey instance with space permissions."""

    class Meta:  # noqa: D106
        model = NapseAPIKey
        fields: ClassVar[list[str]] = [
            "name",
            "prefix",
            "is_master_key",
            "revoked",
            "description",
        ]

    def to_representation(self, instance: NapseAPIKey | None = None) -> dict[str, any]:
        """Convert the instance into a dictionary."""
        representation = super().to_representation(instance)
        instance = instance or self._instance
        representation["permissions"] = []
        space = self._kwargs.get("space", None)
        if space is None:
            return representation

        for permission in instance.permissions.filter(space__uuid=space):
            representation["permissions"].append(permission.permission_type)
        return representation
