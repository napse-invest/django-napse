from django_napse.api.permissions.serializers import PermissionSerializer
from django_napse.auth.models import NapseAPIKey
from django_napse.utils.serializers import BoolField, Serializer, StrField


class NapseAPIKeySerializer(Serializer):
    """Serialize a NapseAPIKey instance."""

    Model = NapseAPIKey

    name = StrField()
    prefix = StrField()
    permissions = PermissionSerializer(many=True)
    is_master_key = BoolField()
    revoked = BoolField()
    description = StrField()


class NapseAPIKeySpaceSerializer(Serializer):
    """Serialize a NapseAPIKey instance with space permissions."""

    Model = NapseAPIKey
    name = StrField()
    prefix = StrField()
    is_master_key = BoolField()
    revoked = BoolField()
    description = StrField()

    def to_value(self, instance: NapseAPIKey | None = None) -> dict[str, any]:
        """Convert the instance into a dictionary."""
        representation = super().to_value(instance)
        instance = instance or self._instance
        representation["permissions"] = []
        space = self._kwargs.get("space", None)
        if space is None:
            return representation

        for permission in instance.permissions.filter(space__uuid=space):
            representation["permissions"].append(permission.permission_type)
        return representation
