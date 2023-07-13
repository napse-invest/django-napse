from django.apps import apps
from django.db import models


class ConnectionManager(models.Manager):
    def create(self, user, bot, enabled=True):
        connection = self.model(user=user, bot=bot, enabled=enabled)
        ConnectionWallet = apps.get_model("ConnectionWallet")
        connection.save()
        bot.init_specific_args(connection)
        ConnectionWallet = apps.get_model("ConnectionWallet")
        ConnectionWallet.objects.create(
            title=f"{user.username} - {bot.name}",
            owner=connection,
            currencies=[(bot.base, 0), (bot.quote, 0)],
            exchange=bot.exchange,
        )
        return connection
