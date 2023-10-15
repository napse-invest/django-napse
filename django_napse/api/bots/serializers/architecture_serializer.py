from rest_framework import serializers

from django_napse.core.models.bots.architecture import Architecture


class ArchitectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Architecture
        fields = "__all__"
        read_only_fields = [
            "id",
        ]
