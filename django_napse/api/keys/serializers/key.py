from rest_framework import serializers

from django_napse.api.permissions.serializers import PermissionSerializer
from django_napse.auth.models import NapseAPIKey


class NapseAPIKeySerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = NapseAPIKey
        fields = [
            "name",
            "prefix",
            "permissions",
            "is_master_key",
            "revoked",
            "description",
        ]


class NapseAPIKeySpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NapseAPIKey
        fields = [
            "name",
            "prefix",
            "is_master_key",
            "revoked",
            "description",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["permissions"] = []
        for permission in instance.permissions.filter(space__uuid=self.context["space"]):
            representation["permissions"].append(permission.permission_type)
        return representation
