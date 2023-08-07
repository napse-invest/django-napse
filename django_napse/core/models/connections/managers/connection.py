from django.apps import apps
from django.db import models


class ConnectionManager(models.Manager):
    def create(self, space, bot, enabled=True):
        ConnectionWallet = apps.get_model("django_napse_core", "ConnectionWallet")

        connection = self.model(space=space, bot=bot, enabled=enabled)
        connection.save()
        # bot.init_specific_args(connection)
        ConnectionWallet.objects.create(
            title=f"{space.name} - {bot.name}",
            owner=connection,
        )
        return connection
