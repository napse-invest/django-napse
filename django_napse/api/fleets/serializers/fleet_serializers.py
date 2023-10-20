from rest_framework import serializers
from rest_framework.fields import empty

from django_napse.api.bots.serializers import BotSerializer
from django_napse.core.models import ConnectionWallet, Fleet


class FleetSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField(read_only=True)
    bot_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Fleet
        fields = [
            "name",
            # read-only
            "uuid",
            "value",
            "bot_count",
        ]
        read_only_fields = [
            "uuid",
            "value",
            "bot_count",
        ]

    def __init__(self, instance=None, data=empty, space=None, **kwargs):
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def get_value(self, instance):
        return instance.value(space=self.space)

    def get_bot_count(self, instance):
        return instance.bots.count()


class FleetDetailSerializer(serializers.Serializer):
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
        ]

    def __init__(self, instance=None, data=empty, space=None, **kwargs):
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def get_statistics(self, instance):
        return instance.get_stats()

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

        wallets = ConnectionWallet.objects.filter(owner__owner=self.space.wallet, owner__bot__in=instance.bots)
        merged_wallet: list[dict[str, str | float]] = []

        for wallet in wallets:
            for currency in wallet.currencies.all():
                index = _search_ticker(currency.ticker, merged_wallet)
                _update_merged_wallet(index, currency, merged_wallet)

        return merged_wallet

    def save(self, **kwargs):
        error_msg: str = "Impossible to update a fleet through the detail serializer."
        raise ValueError(error_msg)
