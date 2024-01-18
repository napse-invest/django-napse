from rest_framework import serializers
from rest_framework.fields import empty

from django_napse.api.orders.serializers import OrderSerializer
from django_napse.api.wallets.serializers import WalletSerializer
from django_napse.core.models import Bot, BotHistory, ConnectionWallet, Order


class BotSerializer(serializers.ModelSerializer):
    # strategy = StrategySerializer()
    delta = serializers.SerializerMethodField(read_only=True)
    space = serializers.SerializerMethodField(read_only=True)
    exchange_account = serializers.CharField(source="exchange_account.uuid", read_only=True)
    fleet = serializers.CharField(source="fleet.uuid", read_only=True)

    class Meta:
        model = Bot
        fields = [
            "name",
            "uuid",
            "value",
            "delta",
            "fleet",
            "space",
            "exchange_account",
        ]
        read_only_fields = [
            "uuid",
            "value",
            "delta",
            "space",
        ]

    def __init__(self, instance=None, data=empty, space=None, **kwargs):
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def get_delta(self, instance) -> float:
        """Delta on the last 30 days."""
        try:
            history = BotHistory.objects.get(owner=instance)
        except BotHistory.DoesNotExist:
            return 0
        return history.get_delta()

    def get_space(self, instance):
        if self.space is None:
            return None
        return self.space.uuid


class BotDetailSerializer(serializers.ModelSerializer):
    delta = serializers.SerializerMethodField(read_only=True)
    space = serializers.SerializerMethodField(read_only=True)
    exchange_account = serializers.CharField(source="exchange_account.uuid", read_only=True)
    fleet = serializers.CharField(source="fleet.uuid", read_only=True)

    statistics = serializers.SerializerMethodField(read_only=True)
    wallet = serializers.SerializerMethodField(read_only=True)
    orders = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bot
        fields = [
            "name",
            "uuid",
            "value",
            "statistics",
            "wallet",
            "fleet",
            "space",
            "exchange_account",
        ]
        read_only_fields = [
            "uuid",
            "value",
            "statistics",
            "wallet",
            "space",
        ]

    def __init__(self, instance=None, data=empty, space=None, **kwargs):
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def get_delta(self, instance) -> float:
        """Delta on the last 30 days."""
        try:
            history = BotHistory.objects.get(owner=instance)
        except BotHistory.DoesNotExist:
            return 0
        return history.get_delta()

    def get_space(self, instance):
        if self.space is None:
            return None
        return self.space.uuid

    def get_wallet(self, instance):
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

        if self.space is not None:
            wallet = ConnectionWallet.objects.get(
                owner__owner=self.space.wallet,
                owner__bot=instance,
            )
            return WalletSerializer(wallet).data

        wallets = [connection.wallet for connection in instance.connections.all()]
        merged_wallet: list[dict[str, str | float]] = []

        for wallet in wallets:
            for currency in wallet.currencies.all():
                index = _search_ticker(currency.ticker, merged_wallet)
                _update_merged_wallet(index, currency, merged_wallet)

        return merged_wallet

    def get_orders(self, instance):
        if self.space is None:
            return OrderSerializer(
                Order.objects.filter(connection__bot=instance),
                many=True,
            ).data
        return OrderSerializer(
            Order.objects.filter(
                connection__bot=instance,
                connection__owner__owner=self.space.wallet,
            ),
            many=True,
        ).data
