from rest_framework import serializers

from django_napse.api.permissions.serializers import PermissionSerializer
from django_napse.auth.models import NapseAPIKey


class NapseAPIKeySerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = NapseAPIKey
        fields = "__all__"
