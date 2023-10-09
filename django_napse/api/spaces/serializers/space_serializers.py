from rest_framework import serializers

from django_napse.api.fleets.serializers import FleetSerializer
from django_napse.core.models import NapseSpace


class SpaceSerializer(serializers.ModelSerializer):
    fleet_count = serializers.SerializerMethodField(read_only=True)
    exchange_account = serializers.CharField(source="exchange_account.uuid", read_only=True)

    class Meta:
        model = NapseSpace
        fields = [
            "name",
            # read-only
            "uuid",
            "value",
            "fleet_count",
            "exchange_account",
        ]
        read_only_fields = [
            "uuid",
            "value",
            "fleet_count",
            "exchange_account",
        ]

    def get_fleet_count(self, instance) -> int:
        return instance.fleets.count()


class SpaceDetailSerializer(serializers.ModelSerializer):
    fleets = FleetSerializer(many=True, read_only=True)
    exchange_account = serializers.CharField(source="exchange_account.uuid", read_only=True)

    class Meta:
        model = NapseSpace
        fields = [
            "name",
            "description",
            # read-only
            "uuid",
            "value",
            "created_at",
            "fleets",
            "exchange_account",
        ]
        read_only_fields = [
            "uuid",
            "value",
            "fleet",
            "created_at",
            "exchange_account",
        ]
