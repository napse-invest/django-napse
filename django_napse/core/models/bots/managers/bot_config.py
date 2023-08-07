from django.db import models

from django_napse.utils.errors import BotConfigError


class BotConfigManager(models.Manager):
    def create(
        self,
        space,
        immutable: bool = False,
        settings=None,
    ):
        settings = settings or {}
        for setting in self.model._meta.get_fields():
            if setting.name.startswith("setting_"):
                try:
                    settings[setting.name[8:]]
                except KeyError as e:
                    error_msg = f"Missing setting: {setting.name[8:]}"
                    raise BotConfigError.MissingSettingError(error_msg) from e
        if not immutable:
            try:
                self.model.objects.get(
                    space=space,
                    immutable=immutable,
                    **{f"setting_{setting_name}": setting_value for setting_name, setting_value in settings.items()},
                )
            except self.model.DoesNotExist:
                pass
            else:
                error_msg = "This BotConfig already exists in this space."
                raise BotConfigError.DuplicateBotConfig(error_msg)
        config = self.model(
            space=space,
            immutable=immutable,
            **{f"setting_{setting_name}": setting_value for setting_name, setting_value in settings.items()},
        )
        config.save()
        return config
