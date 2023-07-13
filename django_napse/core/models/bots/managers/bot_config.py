from django.apps import apps
from django.db import models

from django_napse.utils.errors import BotConfigError


class BotConfigManager(models.Manager):
    def create(
        self,
        space,
        bot_type: str,
        immutable: bool = False,
        **settings,
    ):
        BotModel = apps.get_model("django_napse_core", bot_type)
        for key in BotModel.to_hash_attributes:
            if key not in settings:
                error_msg = f"Missing required argument: {key}"
                raise BotConfigError.MissingSettingError(error_msg)

        bot_hash = hex(BotModel.hash_from_attributes(**settings))
        if not immutable:
            try:
                self.model.objects.get(space=space, bot_hash=bot_hash)
            except self.model.DoesNotExist:
                pass
            else:
                error_msg = "This BotConfig already exists in this space."
                raise BotConfigError.DuplicateBotConfig(error_msg)
        config = self.model(
            bot_type=bot_type,
            bot_hash=bot_hash,
            space=space,
            immutable=immutable,
        )
        config.save()
        BotConfigSetting = apps.get_model("django_napse_core", "BotConfigSetting")
        for key, value in settings.items():
            BotConfigSetting.objects.create(
                bot_config=config,
                key=key,
                value=str(value),
                target_type=str(value.__class__.__name__),
            )

        return config
