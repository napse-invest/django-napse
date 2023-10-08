from rest_framework import serializers

from django_napse.api.fleets.serializers import FleetSerializer
from django_napse.core.models import NapseSpace


class SpaceSerializer(serializers.ModelSerializer):
    fleet_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = NapseSpace
        fields = [
            "name",
            # read-only
            "id",
            "value",
            "fleet_count",
        ]
        read_only_fields = [
            "id",
            "value",
            "fleet_count",
        ]

    def get_fleet_count(self, instance) -> int:
        return instance.fleets.count()


class SpaceDetailSerializer(serializers.ModelSerializer):
    fleets = FleetSerializer(many=True, read_only=True)

    class Meta:
        model = NapseSpace
        fields = [
            "name",
            "description",
            # read-only
            "id",
            "value",
            "created_at",
            "fleets",
        ]
        read_only_fields = [
            "id",
            "value",
            "fleet",
            "created_at",
        ]
