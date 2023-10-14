from rest_framework import serializers

from django_napse.auth.models import KeyPermission


class PermissionSerializer(serializers.ModelSerializer):
    space = serializers.CharField(source="space.uuid")

    class Meta:
        model = KeyPermission
        fields = ["uuid", "permission_type", "approved", "space"]
