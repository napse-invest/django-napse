from rest_framework import serializers
from rest_framework.fields import empty

from django_napse.api.bots.serializers import BotSerializer
from django_napse.api.fleets.serializers.cluster_serialisers import ClusterFormatterSerializer
from django_napse.core.models import ConnectionWallet, Fleet, FleetHistory, NapseSpace, SpaceWallet


class FleetSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField(read_only=True)
    bot_count = serializers.SerializerMethodField(read_only=True)
    clusters = ClusterFormatterSerializer(
        write_only=True,
        many=True,
        required=True,
    )
    space = serializers.UUIDField(write_only=True, required=True)
    delta = serializers.SerializerMethodField(read_only=True)
    exchange_account = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Fleet
        fields = [
            "name",
            # write-only
            "clusters",
            "space",
            # read-only
            "uuid",
            "value",
            "bot_count",
            "delta",
            "exchange_account",
        ]
        read_only_fields = [
            "uuid",
            "exchange_account",
        ]

    def __init__(self, instance=None, data=empty, space=None, **kwargs):
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def get_value(self, instance):
        if self.space is None:
            return instance.value
        return instance.space_frame_value(space=self.space)

    def get_bot_count(self, instance):
        return instance.bot_count(space=self.space)

    def get_delta(self, instance) -> float:
        """Delta on the last 30 days."""
        try:
            history = FleetHistory.objects.get(owner=instance)
        except FleetHistory.DoesNotExist:
            return 0
        return history.get_delta()

    def get_exchange_account(self, instance):
        return instance.exchange_account.uuid

    def validate(self, attrs):
        data = super().validate(attrs)

        try:
            self.space = NapseSpace.objects.get(uuid=attrs.pop("space"))
            print("get space", self.space)
        except NapseSpace.DoesNotExist:
            error_msg: str = "Space does not exist."
            raise serializers.ValidationError(error_msg) from None

        data["exchange_account"] = self.space.exchange_account
        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.space is not None:
            data["space"] = self.space.uuid

        return data

    def create(self, validated_data):
        return Fleet.objects.create(**validated_data)


class FleetDetailSerializer(serializers.ModelSerializer):
    wallet = serializers.SerializerMethodField(read_only=True)
    statistics = serializers.SerializerMethodField(read_only=True)
    bots = BotSerializer(many=True, read_only=True)

    class Meta:
        model = Fleet
        fields = [
            "uuid",
            "name",
            "created_at",
            "statistics",
            "wallet",
            "bots",
            "exchange_account",
        ]

    def __init__(self, instance=None, data=empty, space=None, **kwargs):
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def get_statistics(self, instance):
        return instance.get_stats()

    def get_wallet(self, instance):
        # Method not tested, high chance of being buggy
        def _search_ticker(ticker: str, merged_wallet) -> int | None:
            """Return the index of the currency in the list if found, None otherwise."""
            for i, currency in enumerate(merged_wallet):
                if currency.get("ticker").ticker == ticker:
                    return i
            return None

        def _update_merged_wallet(index: int, currency: str, merged_wallet) -> None:
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.space is not None:
            data["space"] = self.space.uuid
        return data

    def save(self, **kwargs):
        error_msg: str = "Impossible to update a fleet through the detail serializer."
        raise serializers.ValidationError(error_msg)


class FleetMoneyFlowSerializer(serializers.Serializer):
    amount = serializers.FloatField(write_only=True, required=True)
    ticker = serializers.CharField(write_only=True, required=True)

    def __init__(self, instance=None, data=empty, side=None, space=None, **kwargs):
        if side is None or side not in ["INVEST", "WITHDRAW"]:
            error_msg: str = "Side is required."
            raise ValueError(error_msg)
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def validate(self, attrs):
        """Check if the wallet has enough money to invest."""
        if not self.space.testing:
            error_msg: str = "Investing in real is not allowed yet."
            raise serializers.ValidationError(error_msg)

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

    def save(self, **kwargs):
        """Make the transaction."""
        amount = self.validated_data["amount"]
        ticker = self.validated_data["ticker"]
        self.instance.invest(self.space, amount, ticker)
