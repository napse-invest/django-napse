from django.apps import apps
from django.db import models


class ExchangeAccountManager(models.Manager):
    def create(
        self,
        exchange,
        testing: bool,
        name: str,
        description: str = "",
        **kwargs,
    ):
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
