from django.db import models


class BotManager(models.Manager):
    def create(
        self,
        name,
        strategy,
    ):
        return
