from rest_framework import serializers

from django_napse.auth.models import KeyPermission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyPermission
        fields = "__all__"
