from django.apps import apps
from django.db import models


class ConnectionManager(models.Manager):
    """Define how the Connection.objects works."""

    def create(self, owner: "Wallet", bot: "Bot") -> "Connection":  # noqa: F821
        ConnectionWallet = apps.get_model("django_napse_core", "ConnectionWallet")

        connection = self.model(owner=owner, bot=bot)
        connection.save()
        # bot.init_specific_args(connection)  # noqa: ERA001
        ConnectionWallet.objects.create(
            title=f"Connection between {owner.title} - {bot.name}",
            owner=connection,
        )
        return connection
