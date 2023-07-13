import json
import logging

import environ
from django.conf import settings

from django_napse.utils.constants import EXCHANGES
from django_napse.utils.errors import NapseError

logger = logging.getLogger("django_napse")

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

    # if "NAPSE_EXCHANGE_CONFIGS" not in settings.__dir__():
    #     logger.warning("WARNING: NAPSE_EXCHANGE_CONFIGS not found in settings. Creating them now.")
    #     settings.NAPSE_EXCHANGE_CONFIGS = {
    #         "BINANCE": {
    #             "description": "Binance exchange. More info: https://www.binance.com/en",
    #         },
    #     }
    if list(settings.NAPSE_EXCHANGE_CONFIGS.keys()) != list(EXCHANGES):
        error_msg = "NAPSE_EXCHANGE_CONFIGS does not match the list of exchanges. Can't start the server."
        raise NapseError.SettingsError(error_msg)


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
    def IS_IN_PIPELINE(self):
        return environ.Env().bool("IS_IN_PIPELINE", default=False)


napse_settings = DjangoNapseSettings()
