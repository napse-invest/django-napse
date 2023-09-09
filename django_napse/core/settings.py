import json
import logging

import environ
from django.conf import settings

from django_napse.utils.constants import EXCHANGES
from django_napse.utils.errors import NapseError

logger = logging.getLogger("django_napse")


class DjangoNapseSettings:
    @property
    def NAPSE_EXCHANGE_CONFIGS(self):
        return getattr(
            settings,
            "NAPSE_EXCHANGE_CONFIGS",
            {
                "BINANCE": {
                    "description": "Binance exchange. More info: https://www.binance.com/en",
                },
            },
        )

    @property
    def NAPSE_IS_IN_PIPELINE(self):
        return environ.Env().bool("NAPSE_IS_IN_PIPELINE", default=False)

    @property
    def NAPSE_SECRETS_FILE_PATH(self):
        return getattr(settings, "NAPSE_SECRETS_FILE_PATH", "secrets.json")

    @property
    def NAPSE_EXCHANGES_TO_TEST(self):
        return getattr(settings, "NAPSE_EXCHANGES_TO_TEST", ["BINANCE"])


napse_settings = DjangoNapseSettings()

if settings.configured:
    if "django_celery_beat" not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS += ("django_celery_beat",)

    if "NAPSE_SECRETS_FILE_PATH" not in settings.__dir__():
        error_msg = "NAPSE_SECRETS_FILE_PATH not found in settings. Please add it to your settings file."
        raise NapseError.SettingsError(error_msg)
    else:
        try:
            with open(settings.NAPSE_SECRETS_FILE_PATH) as secrets_file:
                secrets = json.load(secrets_file)
        except FileNotFoundError:
            warning = f"WARNING: No secrets file found at {settings.NAPSE_SECRETS_FILE_PATH}. Creating one now."
            logger.warning(warning)
            with open(settings.NAPSE_SECRETS_FILE_PATH, "w") as secrets_file:
                json.dump({"Exchange Accounts": {}}, secrets_file)

    if {*list(napse_settings.NAPSE_EXCHANGE_CONFIGS.keys())} != set(EXCHANGES):
        error_msg = "NAPSE_EXCHANGE_CONFIGS does not match the list of exchanges. Can't start the server."
        raise NapseError.SettingsError(error_msg)
