import uuid
from json import loads

from rest_framework import serializers

from django_napse.api.fleets.serializers import FleetSerializer
from django_napse.api.wallets.serializers.wallet_serializers import WalletSerializer
from django_napse.core.models import ExchangeAccount, NapseSpace, SpaceHistory


class SpaceSerializer(serializers.ModelSerializer):
    exchange_account = serializers.CharField(source="exchange_account.uuid")
    delta = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = NapseSpace
        fields = [
            "name",
            "description",
            "exchange_account",
            # read-only
            "uuid",
            "value",
            "delta",
        ]
        read_only_fields = [
            "uuid",
            "value",
            "delta",
        ]

    def get_delta(self, instance) -> float:
        """Delta on the last 30 days."""
        try:
            history = SpaceHistory.objects.get(owner=instance)
        except SpaceHistory.DoesNotExist:
            return 0
        return history.get_delta()

    def create(self, validated_data):
        try:
            uuid.UUID(str(validated_data["exchange_account"]["uuid"]))
        except ValueError:
            error_msg: str = "Invalid UUID"
            raise serializers.ValidationError(error_msg) from None
        try:
            exchange_account = ExchangeAccount.objects.get(uuid=validated_data["exchange_account"]["uuid"])
        except ExchangeAccount.DoesNotExist:
            error_msg: str = "Exchange Account does not exist"
            raise serializers.ValidationError(error_msg) from None

        return NapseSpace.objects.create(
            name=validated_data["name"],
            description=validated_data["description"],
            exchange_account=exchange_account,
        )


class SpaceDetailSerializer(serializers.ModelSerializer):
    fleets = FleetSerializer(many=True, read_only=True)
    exchange_account = serializers.CharField(source="exchange_account.uuid", read_only=True)
    statistics = serializers.SerializerMethodField(read_only=True)
    wallet = WalletSerializer(read_only=True)
    history = serializers.SerializerMethodField(read_only=True)

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
            "history",
            "fleets",
        ]
        read_only_fields = [
            "uuid",
            "exchange_account",
            "created_at",
            "statistics",
            "wallet",
            "history",
            "fleet",
        ]

    def get_statistics(self, instance) -> dict:
        return instance.get_stats()

    def get_history(self, instance) -> list:
        try:
            history = SpaceHistory.objects.get(owner=instance)
        except SpaceHistory.DoesNotExist:
            return []

        return loads(history.to_dataframe().to_json(orient="records"))
