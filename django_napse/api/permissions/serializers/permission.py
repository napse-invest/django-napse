from typing import ClassVar

from rest_framework import serializers

from django_napse.auth.models import KeyPermission


class PermissionSerializer(serializers.ModelSerializer):
    """Serialize a permission instance."""

    space = serializers.CharField(source="space.uuid")

    class Meta:  # noqa: D106
        model = KeyPermission
        fields: ClassVar[list[str]] = [
            "uuid",
            "permission_type",
            "approved",
            "space",
        ]
