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
            "exchange_account",
            # read-only
            "uuid",
            "value",
            "fleet_count",
        ]
        read_only_fields = [
            "uuid",
            "value",
            "fleet_count",
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
            "exchange_account",
            "created_at",
            "statistics",
            "wallet",
            "fleets",
        ]
        read_only_fields = [
            "uuid",
            "exchange_account",
            "created_at",
            "statistics",
            "wallet",
            "fleet",
        ]

    def get_statistics(self, instance) -> dict:
        return instance.get_stats()
