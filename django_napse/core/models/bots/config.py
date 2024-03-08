import uuid

from django.db import models

from django_napse.core.models.bots.managers.bot_config import BotConfigManager
from django_napse.core.models.bots.strategy import Strategy
from django_napse.utils.findable_class import FindableClass


class BotConfig(models.Model, FindableClass):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    space = models.ForeignKey("Space", on_delete=models.CASCADE, related_name="bot_configs")
    immutable = models.BooleanField(default=False)

    objects = BotConfigManager()

    def __str__(self) -> str:  # pragma: no cover
        return f"BOT CONFIG: {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}BotConfig: ({self.pk=})\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.space=}\n"
        string += f"{beacon}Settings:\n"
        for setting, value in self.settings.items():
            string += f"{beacon}\t" + setting + f"={value}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def settings(self):
        settings = {}
        for setting in self._meta.get_fields():
            if setting.name.startswith("setting_"):
                settings[setting.name[8:]] = getattr(self, setting.name)
        return settings

    @property
    def strategy(self):
        return Strategy.objects.get(config=self).find()

    def duplicate_immutable(self):
        return self.__class__.objects.create(
            space=self.space,
            immutable=True,
            settings=self.settings,
        )

    def duplicate_other_space(self, space):
        if space == self.space:
            error_msg = "The space of the new bot config must be different from the space of the original bot config."
            raise ValueError(error_msg)
        return self.__class__.objects.create(
            space=space,
            immutable=True,
            settings=self.settings,
        )
