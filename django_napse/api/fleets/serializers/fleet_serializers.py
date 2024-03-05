from rest_framework import serializers

from django_napse.api.bots.serializers import BotSerializer
from django_napse.api.fleets.serializers.cluster_serialisers import ClusterFormatterSerializer
from django_napse.core.models import ConnectionWallet, Fleet, FleetHistory, Space, SpaceWallet
from django_napse.utils.serializers import DatetimeField, FloatField, MethodField, Serializer, StrField, UUIDField


class FleetSerializer(Serializer):
    """Serialize fleet instance.

    Can be use with many fleet instances.
    """

    Model = Fleet

    uuid = UUIDField()
    name = StrField()
    value = MethodField()
    bot_count = MethodField()
    clusters = ClusterFormatterSerializer(many=True, required=True)
    delta = MethodField()
    exchange_account = UUIDField(source="exchange_account.uuid")

    def __init__(
        self,
        instance: Fleet | None = None,
        data: dict[str, any] | None = None,
        space: Space | None = None,
        **kwargs: dict[str, any],
    ) -> None:
        """."""
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def get_value(self, instance: Fleet) -> float:
        """Return fleet's value, can be space contained if space is given in serializer."""
        if self.space is None:
            return instance.value
        return instance.space_frame_value(space=self.space)

    def get_bot_count(self, instance: Fleet) -> int:
        """Return fleet's bot count, can be space contained if space is given in serializer."""
        return instance.bot_count(space=self.space)

    def get_delta(self, instance: Fleet) -> float:
        """Delta on the last 30 days."""
        try:
            history = FleetHistory.objects.get(owner=instance)
        except FleetHistory.DoesNotExist:
            return 0
        return history.get_delta()

    def validate(self, attrs: dict[str, any]) -> dict[str, any]:
        """Validation process for Fleet creation."""
        data = super().validate(attrs)
        # Space is required only to make the 1st automatic empty invest when creating a fleet (logic is in the view)
        if "space" not in attrs:
            error_msg: str = "Space is required."
            raise serializers.ValidationError(error_msg)

        try:
            self.space = Space.objects.get(uuid=attrs.pop("space"))
            print("get space", self.space)
        except Space.DoesNotExist:
            error_msg: str = "Space does not exist."
            raise serializers.ValidationError(error_msg) from None

        data["exchange_account"] = self.space.exchange_account
        return data

    def to_value(self, instance: Fleet) -> dict[str, any]:
        """Serialize Fleet instance."""
        data = super().to_value(instance)
        if self.space is not None:
            for data_instane in data:
                data_instane["space"] = self.space.uuid

        return data


class FleetDetailSerializer(Serializer):
    """Deep serialization of a fleet instance.

    Use this serializer for endpoints details only.
    """

    Model = Fleet
    read_only = True

    uuid = UUIDField()
    name = StrField()
    statistics = MethodField()
    wallet = MethodField()
    bots = BotSerializer(many=True)
    created_at = DatetimeField()
    exchange_account = UUIDField(source="exchange_account.uuid")

    def __init__(
        self,
        instance: Fleet | None = None,
        data: dict[str, any] | None = None,
        space: Space | None = None,
        **kwargs: dict[str, any],
    ) -> None:
        """."""
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def get_statistics(self, instance: Fleet) -> dict[str, str | int | float]:
        """Return Fleet's stats."""
        return instance.get_stats()

    def get_wallet(self, instance: Fleet) -> list[dict[str, float | str]] | None:
        """Return an aggregated wallet for a given space.

        Return None if space is not given.
        """

        # Method not tested, high chance of being buggy
        def _search_ticker(ticker: str, merged_wallet: list[dict[str, str | float]]) -> int | None:
            """Return the index of the currency in the list if found, None otherwise."""
            for i, currency in enumerate(merged_wallet):
                if currency.get("ticker").ticker == ticker:
                    return i
            return None

        def _update_merged_wallet(index: int, currency: str, merged_wallet: list[dict[str, str | float]]) -> None:
            """Update the merged wallet with the new currency."""
            if index is None:
                merged_wallet.append(
                    {
                        "ticker": currency.ticker,
                        "amount": currency.amount,
                        "mbp": currency.mbp,
                    },
                )
            else:
                merged_wallet[index]["amount"] += currency.amount

        if self.space is None:
            return None
        wallets = ConnectionWallet.objects.filter(owner__owner=self.space.wallet, owner__bot__in=instance.bots)
        merged_wallet: list[dict[str, str | float]] = []

        for wallet in wallets:
            for currency in wallet.currencies.all():
                index = _search_ticker(currency.ticker, merged_wallet)
                _update_merged_wallet(index, currency, merged_wallet)

        return merged_wallet

    def to_value(self, instance: Fleet | None = None) -> dict[str, any]:
        """Return Fleet's serialization."""
        print(f"{self._many=}", self)
        data = super().to_value(instance)
        if self.space is not None:
            data["space"] = self.space.uuid
        return data


class FleetMoneyFlowSerializer(Serializer):
    """."""

    amount = FloatField(required=True)
    ticker = StrField(required=True)

    def __init__(
        self,
        side: str,
        instance: Fleet | None = None,
        data: dict[str, any] | None = None,
        space: Space | None = None,
        **kwargs: dict[str, any],
    ) -> None:
        """."""
        self.side = side
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def _invest_validate(self, attrs: dict[str, any]) -> dict[str, any]:
        if self.space.testing:
            space_wallet = self.space.wallet
            try:
                currency: SpaceWallet = space_wallet.currencies.get(ticker=attrs["ticker"])
            except SpaceWallet.DoesNotExist:
                error_msg: str = f"{attrs['ticker']} does not exist in space ({self.space.name})."
                raise serializers.ValidationError(error_msg) from None

            if currency.amount < attrs["amount"]:
                error_msg: str = f"Not enough {currency.ticker} in the wallet."
                raise serializers.ValidationError(error_msg)

            return attrs

        error_msg: str = "Real invest is not implemented yet."
        raise NotImplementedError(error_msg)

    def _withdraw_validate(self, attrs: dict[str, any]) -> dict[str, any]:  # noqa: ARG002
        if self.space.testing:
            error_msg: str = "Withdraw is not implemented yet."
            raise NotImplementedError(error_msg)

        error_msg: str = "Real withdraw is not implemented yet."
        raise NotImplementedError(error_msg)

    def validate(self, attrs: dict[str, any]) -> dict[str, any]:
        """Check if the wallet has enough money to invest."""
        match self.side.upper():
            case "INVEST":
                return self._invest_validate(attrs)
            case "WITHDRAW":
                return self._withdraw_validate(attrs)
            case _:
                error_msg: str = "Invalid side."
                raise ValueError(error_msg)

    def save(self) -> None:
        """Make the transaction."""
        amount = self.validated_data["amount"]
        ticker = self.validated_data["ticker"]
        self.instance.invest(self.space, amount, ticker)
