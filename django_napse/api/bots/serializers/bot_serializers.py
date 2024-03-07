from typing import ClassVar
from uuid import UUID

from rest_framework import serializers

from django_napse.api.orders.serializers import OrderSerializer
from django_napse.api.wallets.serializers import WalletSerializer
from django_napse.core.models import Bot, BotHistory, ConnectionWallet, Order, Space


class BotSerializer(serializers.ModelSerializer):
    """Serialize bot instances."""

    delta = serializers.SerializerMethodField(read_only=True)
    space = serializers.SerializerMethodField(read_only=True)
    value = serializers.SerializerMethodField(read_only=True)
    exchange_account = serializers.SerializerMethodField(read_only=True)
    fleet = serializers.CharField(source="fleet.uuid", read_only=True)

    class Meta:  # noqa: D106
        model = Bot
        fields: ClassVar = [
            "name",
            "uuid",
            "value",
            "delta",
            "fleet",
            "space",
            "exchange_account",
        ]
        read_only_fields: ClassVar = [
            "uuid",
            "value",
            "delta",
            "space",
        ]

    def __init__(self, *args: list[any], space: Space | None = None, **kwargs: dict[str, any]) -> None:
        """Add space to the serializer and run the default constructor."""
        self.space = space
        super().__init__(*args, **kwargs)

    def get_delta(self, instance: Bot) -> float:
        """Delta on the last 30 days."""
        try:
            history = BotHistory.objects.get(owner=instance)
        except BotHistory.DoesNotExist:
            return 0
        return history.get_delta()

    def get_space(self, instance: Bot) -> UUID | None:  # noqa: ARG002
        """Return the space used for the space containerization."""
        if self.space is None:
            return None
        print("UUID", type(self.space.uuid))
        return self.space.uuid

    def get_exchange_account(self, instance: Bot) -> UUID | None:
        """Return the exchange account of the bot if it exists."""
        if not instance.is_in_fleet and not instance.is_in_simulation:
            return None
        return instance.exchange_account.uuid

    def get_value(self, instance: Bot) -> float:
        """Return bot's value."""
        return instance.value(space=self.space)

    def create(self, validated_data: dict[str, any]) -> Bot:  # noqa: ARG002
        """Create a bot instance."""
        error_msg: str = "You don't have to create a bot from an endpoint"
        raise ValueError(error_msg)


class BotDetailSerializer(serializers.ModelSerializer):
    """Deep dive in bot's data for serialization."""

    delta = serializers.SerializerMethodField(read_only=True)
    space = serializers.SerializerMethodField(read_only=True)
    value = serializers.SerializerMethodField(read_only=True)
    exchange_account = serializers.CharField(source="exchange_account.uuid", read_only=True)
    fleet = serializers.CharField(source="fleet.uuid", read_only=True)

    statistics = serializers.SerializerMethodField(read_only=True)
    wallet = serializers.SerializerMethodField(read_only=True)
    orders = serializers.SerializerMethodField(read_only=True)

    class Meta:  # noqa: D106
        model = Bot
        fields: ClassVar[list[str]] = [
            "name",
            "uuid",
            "value",
            "delta",
            "statistics",
            "fleet",
            "space",
            "exchange_account",
            "wallet",
            "orders",
        ]
        read_only_fields: ClassVar = fields

    def __init__(self, *args: list[any], space: Space | None = None, **kwargs: dict[str, any]) -> None:
        """Add space to the serializer and run the default constructor."""
        self.space = space
        super().__init__(*args, **kwargs)

    def get_delta(self, instance: Bot) -> float:
        """Delta on the last 30 days."""
        try:
            history = BotHistory.objects.get(owner=instance)
        except BotHistory.DoesNotExist:
            return 0
        return history.get_delta()

    def get_value(self, instance: Bot) -> float:
        """Return bot's value."""
        return instance.value(space=self.space)

    def get_space(self, instance: Bot) -> UUID | None:  # noqa: ARG002
        """Return the space used for the space containerization."""
        if self.space is None:
            return None
        return self.space.uuid

    def get_statistics(self, instance: Bot) -> dict[str, str | int | float]:
        """Return Bot's statistics."""
        return instance.get_stats(space=self.space)

    def get_wallet(self, instance: Bot) -> dict[str, any] | list[dict[str, any]]:
        """Return space's connections wallet of this bot, or return all connections wallets."""
        if self.space is not None:
            wallet = ConnectionWallet.objects.get(
                owner__owner=self.space.wallet,
                owner__bot=instance,
            )
            return WalletSerializer(wallet).data

        wallets = [connection.wallet for connection in instance.connections.all()]
        return WalletSerializer(wallets, many=True).data

    def get_orders(self, instance: Bot) -> list[dict[str, any]]:
        """Return all orders of the bot."""
        if self.space is None:
            return OrderSerializer(
                Order.objects.filter(connection__bot=instance),
                many=True,
            ).data

        return OrderSerializer(
            Order.objects.filter(
                connection__bot=instance,
                connection__owner=self.space.wallet,
            ),
            many=True,
        ).data

    def create(self, validated_data: dict[str, any]) -> Bot:  # noqa: ARG002
        """Create a bot instance."""
        error_msg: str = "You don't have to create a bot from an endpoint"
        raise ValueError(error_msg)

    def update(self, instance: Bot, validated_data: dict[str, any]) -> Bot:  # noqa: ARG002
        """Update a bot instance."""
        error_msg: str = "You don't have to update a bot from an endpoint"
        raise ValueError(error_msg)
