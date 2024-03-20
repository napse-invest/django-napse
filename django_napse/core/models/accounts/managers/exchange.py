from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps
from django.db import models

if TYPE_CHECKING:
    from django_napse.core.models.accounts.exchange import Exchange, ExchangeAccount


class ExchangeAccountManager(models.Manager):
    """Manager for the ExchangeAccount model."""

    def create(
        self,
        exchange: Exchange,
        name: str,
        description: str = "",
        *,
        testing: bool,
        **kwargs: dict[str, any],
    ) -> ExchangeAccount:
        """Create a new exchange account."""
        Space = apps.get_model("django_napse_core", "Space")
        exchange_account = self.model(
            exchange=exchange,
            name=name,
            description=description,
            testing=testing,
            **kwargs,
        )
        exchange_account.save()
        Space.objects.create(
            name=exchange_account.name,
            description=f"This is the main space for the {exchange_account.name} exchange account.",
            exchange_account=exchange_account,
        )
        return exchange_account
