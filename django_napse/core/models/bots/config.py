import uuid

from django.apps import apps
from django.db import models

from django_napse.utils.findable_class import FindableClass


class BotConfig(models.Model, FindableClass):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    space = models.ForeignKey("NapseSpace", on_delete=models.CASCADE, related_name="bot_configs")
    immutable = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"BOT CONFIG: {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}BotConfig: ({self.pk=})\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.bot_type=}\n"
        string += f"{beacon}\t{self.space=}\n"
        string += f"{beacon}Settings:\n"
        if len(self.settings) > 0:
            for setting, value in self.settings.items():
                string += beacon + setting + f"={value}\n"
        else:
            string += f"{beacon}\tNo settings\n"
        if verbose:
            print(string)
        return string

    @property
    def settings(self):
        settings = {}
        for setting in self._meta.get_fields():
            if setting.name.startswith("setting_"):
                settings[setting.name[8:]] = getattr(self, setting.name)
        return settings

    def to_bot(self, **kwargs):
        """Create a bot from the bot config."""
        Bot = apps.get_model("django_napse_core", self.bot_type)
        settings = {key: value for key, value in self.settings.items()}
        return Bot.objects.create(**kwargs, **settings)

    def duplicate_immutable(self):
        return self.__class__.objects.create(
            space=self.space,
            immutable=True,
            **{f"setting_{key}": value for key, value in self.settings.items()},
        )

    def duplicate_other_space(self, space):
        if space == self.space:
            error_msg = "The space of the new bot config must be different from the space of the original bot config."
            raise ValueError(error_msg)
        return self.__class__.objects.create(
            space=space,
            immutable=True,
            **{f"setting_{key}": value for key, value in self.settings.items()},
        )
