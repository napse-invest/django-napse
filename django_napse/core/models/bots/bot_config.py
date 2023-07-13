import uuid

from django.apps import apps
from django.db import models

from django_napse.core.models.bots.managers import BotConfigManager
from django_napse.utils.usefull_functions import process_value_from_type


class BotConfig(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    bot_type = models.CharField(max_length=100)
    bot_hash = models.CharField(max_length=100)
    space = models.ForeignKey("NapseSpace", on_delete=models.CASCADE, related_name="bot_configs")
    immutable = models.BooleanField(default=False)

    objects = BotConfigManager()

    def __str__(self) -> str:  # pragma: no cover
        """Return a string representation of the bot config."""
        return f"BOT CONFIG: {self.pk} - {self.bot_type} - {self.bot_hash}"

    def info(self, verbose=True, beacon=""):  # pragma: no cover
        string = ""
        string += f"{beacon}BotConfig: ({self.pk=})\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.bot_type=}\n"
        string += f"{beacon}\t{self.bot_hash=}\n"
        string += f"{beacon}\t{self.space=}\n"
        settings = self.settings.all()
        string += f"{beacon}Settings:\n"
        if settings.count() > 0:
            for setting in settings:
                string += beacon + setting.info(verbose=False, beacon=beacon + "\t")
        else:
            string += f"{beacon}\tNo settings\n"
        if verbose:
            print(string)
        return string

    def to_bot(self, **kwargs):
        """Create a bot from the bot config."""
        Bot = apps.get_model("django_napse_core", self.bot_type)
        settings = {setting.key: setting.get_value() for setting in self.settings.all()}
        return Bot.objects.create(**kwargs, **settings)

    def duplicate_immutable(self):
        return BotConfig.objects.create(
            space=self.space,
            bot_type=self.bot_type,
            immutable=True,
            **{arg.key: arg.get_value() for arg in self.settings.all()},
        )

    def duplicate_other_space(self, space):
        if space == self.space:
            error_msg = "The space of the new bot config must be different from the space of the original bot config."
            raise ValueError(error_msg)
        return BotConfig.objects.create(
            space=space,
            bot_type=self.bot_type,
            immutable=False,
            **{arg.key: arg.get_value() for arg in self.settings.all()},
        )


class BotConfigSetting(models.Model):
    bot_config = models.ForeignKey(BotConfig, on_delete=models.CASCADE, related_name="settings")
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100)

    def __str__(self) -> str:  # pragma: no cover
        return f"BotConfigSetting: {self.pk} - {self.key} - {self.value}"

    def info(self, verbose=True, beacon=""):  # pragma: no cover
        string = ""
        string += f"{beacon}BotConfigSetting: ({self.pk=})\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.key=} | {self.value=} | {self.target_type=}\n"
        if verbose:
            print(string)
        return string

    def get_value(self):
        """Return the value of the setting, processed according to the target type."""
        return process_value_from_type(self.value, self.target_type)
