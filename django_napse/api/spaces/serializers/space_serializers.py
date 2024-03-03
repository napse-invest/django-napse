import uuid
from json import loads

from rest_framework import serializers

from django_napse.api.fleets.serializers import FleetSerializer
from django_napse.api.wallets.serializers.wallet_serializers import WalletSerializer
from django_napse.core.models import ExchangeAccount, Space, SpaceHistory
from django_napse.utils.serializers import BoolField, DatetimeField, FloatField, MethodField, Serializer, StrField, UUIDField


class SpaceSerializer(Serializer):
    """To serialize & create a space instance."""

    Model = Space

    uuid = UUIDField()
    name = StrField()
    description = StrField()
    testing = BoolField()
    value = FloatField()
    exchange_account = UUIDField(source="exchange_account.uuid")

    delta = MethodField()

    def get_delta(self, instance: Space) -> float:
        """Delta on the last 30 days."""
        try:
            history = SpaceHistory.objects.get(owner=instance)
        except SpaceHistory.DoesNotExist:
            return 0
        return history.get_delta()

    def create(self, validated_data: dict[str, any]) -> Space:
        """Create a space if data are validated."""
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

        return Space.objects.create(
            name=validated_data["name"],
            description=validated_data["description"],
            exchange_account=exchange_account,
        )


class SpaceDetailSerializer(Serializer):
    """Deep serialization of a space instance."""

    Model = Space

    uuid = UUIDField()
    name = StrField()
    description = StrField()
    testing = BoolField()
    exchange_account = StrField(source="exchange_account.uuid")
    fleets = FleetSerializer(many=True)
    statistics = MethodField()
    wallet = WalletSerializer()
    history = MethodField()
    created_at = DatetimeField()

    def get_statistics(self, instance: Space) -> dict:
        """Return statistics of the given space."""
        return instance.get_stats()

    def get_history(self, instance: Space) -> list:
        """Return history of the given space."""
        try:
            history = SpaceHistory.objects.get(owner=instance)
        except SpaceHistory.DoesNotExist:
            return []

        return loads(history.to_dataframe().to_json(orient="records"))


class SpaceMoneyFlowSerializer(Serializer):
    """Serialization for money actions on the given space."""

    amount = FloatField(required=True)
    ticker = StrField(required=True)

    def __init__(
        self,
        side: str,
        instance: Space | None = None,
        data: dict[str, any] | None = None,
        **kwargs: dict[str, any],
    ) -> None:
        """Definie side & initilize the serializer."""
        self.side = side
        super().__init__(instance=instance, data=data, **kwargs)

    def _invest_validate(self, attrs: dict[str, any]) -> dict[str, any]:
        if not self.instance.testing:
            error_msg: str = "Not implemented yet."
            raise NotImplementedError(error_msg)

        # Test invest
        return attrs

    def _withdraw_validate(self, attrs: dict[str, any]) -> dict[str, any]:
        if self.instance.testing:
            error_msg: str = "Not implemented yet."
            raise NotImplementedError(error_msg)

        # Test withdraw
        return attrs

    def validate(self, attrs: dict[str, any]) -> dict[str, any]:
        """Make validation."""
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

    def save(self) -> None:
        """Make validated action on the space."""
        if self.side.upper() == "INVEST":
            self.instance.invest(
                self.validated_data.get("amount"),
                self.validated_data.get("ticker"),
            )
        else:
            self.instance.withdraw(self.amount, self.ticker)
