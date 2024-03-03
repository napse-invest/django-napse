from django_napse.auth.models import KeyPermission
from django_napse.utils.serializers import BoolField, Serializer, StrField, UUIDField


class PermissionSerializer(Serializer):
    """Serialize a permission instance."""

    Model = KeyPermission
    read_only = True

    uuid = UUIDField()
    permission_type = StrField()
    approved = BoolField()
    space = StrField(source="space.uuid")
