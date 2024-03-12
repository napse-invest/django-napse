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
            "testing",
            "value",
            "delta",
        ]
        read_only_fields = [
            "uuid",
            "testing",
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
            "testing",
            "exchange_account",
            "created_at",
            "statistics",
            "wallet",
            "history",
            "fleets",
        ]
        read_only_fields = [
            "uuid",
            "testing",
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


class SpaceMoneyFlowSerializer(serializers.Serializer):
    amount = serializers.FloatField(write_only=True, required=True)
    ticker = serializers.CharField(write_only=True, required=True)

    def __init__(self, side, instance=None, data=serializers.empty, **kwargs):
        self.side = side
        super().__init__(instance=instance, data=data, **kwargs)

    def _invest_validate(self, attrs):
        if not self.instance.testing:
            error_msg: str = "Not implemented yet."
            raise NotImplementedError(error_msg)

        # Test invest
        return attrs

    def _withdraw_validate(self, attrs):
        if self.instance.testing:
            error_msg: str = "Not implemented yet."
            raise NotImplementedError(error_msg)

        # Test withdraw
        return attrs

    def validate(self, attrs):
        if attrs.get("amount") <= 0:
            error_msg: str = "Invalid amount."
            raise serializers.ValidationError(error_msg)

        if attrs.get("ticker") not in self.instance.exchange_account.get_tickers():
            error_msg: str = f"{attrs['ticker']} is not available on {self.instance.exchange_account.exchange.name} exchange."
            raise serializers.ValidationError(error_msg)

        match self.side.upper():
            case "INVEST":
                return self._invest_validate(attrs)
            case "WITHDRAW":
                return self._withdraw_validate(attrs)
            case _:
                error_msg: str = "Invalid side."
                raise ValueError(error_msg)

    def save(self, **kwargs):
        if self.side.upper() == "INVEST":
            self.instance.invest(
                self.validated_data.get("amount"),
                self.validated_data.get("ticker"),
            )
        else:
            self.instance.withdraw(self.amount, self.ticker)
