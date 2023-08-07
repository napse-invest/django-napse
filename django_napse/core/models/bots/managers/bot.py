from django.apps import apps
from django.db import models

from django_napse.utils.errors import BotError


class BotManager(models.Manager):
    def build(
        self,
        space,
        config_type: str,
        config_settings: dict,
        strategy_type: str,
        strategy_settings: dict,
        architechture_type: str,
        architechture_settings: dict,
    ):
        BotConfig = apps.get_model("django_napse_core", config_type)
        Strategy = apps.get_model("django_napse_core", strategy_type)
        Architechture = apps.get_model("django_napse_core", architechture_type)

        config = BotConfig.objects.create(space=space, settings=config_settings)
