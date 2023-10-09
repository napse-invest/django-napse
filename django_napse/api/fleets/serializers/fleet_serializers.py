from rest_framework import serializers
from rest_framework.fields import empty

from django_napse.api.bots.serializers import BotSerializer
from django_napse.api.wallets.serializers import WalletSerializer
from django_napse.core.models import ConnectionWallet, Fleet, Wallet


class FleetSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField(read_only=True)
    bot_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Fleet
        fields = [
            "name",
            # read-only
            "id",
            "value",
            "bot_count",
        ]
        read_only_fields = [
            "id",
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
    value = serializers.SerializerMethodField(read_only=True)
    wallet = serializers.SerializerMethodField(read_only=True)
    statistics = serializers.SerializerMethodField(read_only=True)
    bots = BotSerializer(many=True, read_only=True)

    class Meta:
        model = Fleet
        fields = [
            "id",
            "value",
            "created_at",
            "statistics",
            "wallet",
            "bots",
        ]
        read_only_fields = [
            "id",
            "value",
            "created_at",
            "statistics",
            "wallet",
            "bots",
        ]
        write_only_fields = []

    def __init__(self, instance=None, data=empty, space=None, **kwargs):
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    def get_value(self, instance):
        return instance.value(space=self.space)

    def get_statistics(self, instance):
        return instance.get_stats()

    def get_wallet(self, instance):
        # PUT THIS INTO MODEL ???

        # instance.bots
        wallets = ConnectionWallet.objects.filter(connection__bot__in=instance.bots)

        # Merge currencies
        merged_wallet = Wallet(title="merged_wallet")
        merged_wallet.save()
        merged_wallet_tickers: list[str] = []

        for wallet in wallets:
            for currency in wallet.currencies.all():
                if currency.ticker not in merged_wallet_tickers:
                    merged_wallet_tickers.append(currency.ticker)
                    currency.copy(owner=wallet)
                    continue
                merged_currency = merged_wallet.currencies.get(ticker=currency.ticker)
                merged_currency.amount += currency.amount
                merged_currency.save()

        serialized_wallet = WalletSerializer(merged_wallet).data
        merged_wallet.delete()
        return serialized_wallet
