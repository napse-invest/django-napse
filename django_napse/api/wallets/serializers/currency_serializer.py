from __future__ import annotations

from typing import TYPE_CHECKING

from django_napse.core.models.bots.controller import Controller
from django_napse.utils.serializers import FloatField, MethodField, Serializer, StrField

if TYPE_CHECKING:
    from django_napse.core.models import Currency


class CurrencySerializer(Serializer):
    """Serialize a currency instance."""

    mbp = StrField()
    ticker = StrField()
    amount = FloatField()
    value = MethodField()

    def get_value(self, instance: Currency) -> float:
        """Return market value of the currency."""
        return instance.amount * Controller.get_asset_price(
            exchange_account=instance.wallet.exchange_account,
            base=instance.ticker,
        )
