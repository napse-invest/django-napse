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
        return settings.NAPSE_SECRETS_FILE_PATH

    @property
    def NAPSE_ENV_FILE_PATH(self):
        return settings.NAPSE_ENV_FILE_PATH

    @property
    def NAPSE_EXCHANGES_TO_TEST(self):
        return getattr(settings, "NAPSE_EXCHANGES_TO_TEST", ["BINANCE"])

    @property
    def NAPSE_MASTER_KEY(self):
        return getattr(settings, "NAPSE_MASTER_KEY", "insecure_master_key")


napse_settings = DjangoNapseSettings()

if settings.configured:
    for app in [
        "rest_framework",
        "rest_framework_api_key",
        "django_celery_beat",
        "corsheaders",
    ]:
        if app not in settings.INSTALLED_APPS:
            warning = f"{app} not found in settings.INSTALLED_APPS. Please add it to your settings file."
            logger.warning(warning)
            settings.INSTALLED_APPS += (app,)

    if "REST_FRAMEWORK" not in settings.__dir__():
        warning = "REST_FRAMEWORK not found in settings. Please add it to your settings file."
        logger.warning(warning)
        settings.REST_FRAMEWORK = {
            "DEFAULT_PERMISSION_CLASSES": ["django_napse.api.custom_permissions.HasAdminPermission"],
        }
    for permission in ["django_napse.api.custom_permissions.HasAdminPermission"]:
        if permission not in settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"]:
            warning = f"{permission} not found in settings. Please add it to your settings file."
            logger.warning(warning)

    if "NAPSE_SECRETS_FILE_PATH" not in settings.__dir__():
        warning = "NAPSE_SECRETS_FILE_PATH not found in settings. Please add it to your settings file."
        logger.warning(warning)
    try:
        with open(napse_settings.NAPSE_SECRETS_FILE_PATH) as secrets_file:
            secrets = json.load(secrets_file)
    except FileNotFoundError:
        warning = f"WARNING: No secrets file found at {napse_settings.NAPSE_SECRETS_FILE_PATH}. Creating one now."
        logger.warning(warning)
        with open(napse_settings.NAPSE_SECRETS_FILE_PATH, "w") as secrets_file:
            json.dump({"Exchange Accounts": {}}, secrets_file)

    if "NAPSE_ENV_FILE_PATH" not in settings.__dir__():
        warning = "NAPSE_ENV_FILE_PATH not found in settings. Please add it to your settings file."
        logger.warning(warning)
    try:
        with open(napse_settings.NAPSE_ENV_FILE_PATH) as env_file:
            pass
    except FileNotFoundError:
        warning = f"WARNING: No env file found at {napse_settings.NAPSE_ENV_FILE_PATH}. Creating one now."
        logger.warning(warning)
        with open(napse_settings.NAPSE_ENV_FILE_PATH, "w") as env_file:
            env_file.write("")

    if {*list(napse_settings.NAPSE_EXCHANGE_CONFIGS.keys())} != set(EXCHANGES):
        error_msg = "NAPSE_EXCHANGE_CONFIGS does not match the list of exchanges. Can't start the server."
        raise NapseError.SettingsError(error_msg)
