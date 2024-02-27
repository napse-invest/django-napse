import json
import logging
from pathlib import Path

import environ
from django.conf import settings

from django_napse.utils.constants import EXCHANGES
from django_napse.utils.errors import NapseError

logger = logging.getLogger("django_napse")


class DjangoNapseSettings:
    """Main django_napse settings."""

    @property
    def NAPSE_EXCHANGE_CONFIGS(self) -> dict[str, dict[str, any]]:  # noqa: D102
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
    def NAPSE_IS_IN_PIPELINE(self) -> bool:  # noqa: D102
        return environ.Env().bool("NAPSE_IS_IN_PIPELINE", default=False)

    @property
    def NAPSE_SECRETS_FILE_PATH(self) -> Path:  # noqa: D102
        if isinstance(settings.NAPSE_SECRETS_FILE_PATH, str):
            return Path(settings.NAPSE_SECRETS_FILE_PATH).absolute()

        if isinstance(settings.NAPSE_SECRETS_FILE_PATH, Path):
            return settings.NAPSE_SECRETS_FILE_PATH

        error_msg: str = "NAPSE_SECRETS_FILE_PATH must be a string or a Path object."
        raise ValueError(error_msg)

    @property
    def NAPSE_ENV_FILE_PATH(self) -> Path:  # noqa: D102
        if isinstance(settings.NAPSE_ENV_FILE_PATH, str):
            return Path(settings.NAPSE_ENV_FILE_PATH).absolute()

        if isinstance(settings.NAPSE_ENV_FILE_PATH, Path):
            return settings.NAPSE_ENV_FILE_PATH

        error_msg: str = "NAPSE_ENV_FILE_PATH must be a string or a Path object."
        raise ValueError(error_msg)

    @property
    def NAPSE_EXCHANGES_TO_TEST(self) -> list[str]:  # noqa: D102
        return getattr(settings, "NAPSE_EXCHANGES_TO_TEST", ["BINANCE"])

    @property
    def NAPSE_MASTER_KEY(self) -> str:  # noqa: D102
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
    if not napse_settings.NAPSE_SECRETS_FILE_PATH.exists():
        logger.warning(
            "WARNING: No secrets file found at %s. Creating one now.",
            napse_settings.NAPSE_SECRETS_FILE_PATH,
        )
        secrets_file = napse_settings.NAPSE_SECRETS_FILE_PATH.open("w")
        json.dump({"Exchange Accounts": {}}, secrets_file)
        secrets_file.close()

    if "NAPSE_ENV_FILE_PATH" not in settings.__dir__():
        warning = "NAPSE_ENV_FILE_PATH not found in settings. Please add it to your settings file."
        logger.warning(warning)

    if not napse_settings.NAPSE_ENV_FILE_PATH.exists():
        logger.warning(
            "WARNING: No env file found at %s. Creating one now.",
            napse_settings.NAPSE_ENV_FILE_PATH,
        )
        env_file = napse_settings.NAPSE_ENV_FILE_PATH.open("w")
        env_file.write("")
        env_file.close()

    if {*list(napse_settings.NAPSE_EXCHANGE_CONFIGS.keys())} != set(EXCHANGES):
        error_msg = "NAPSE_EXCHANGE_CONFIGS does not match the list of exchanges. Can't start the server."
        raise NapseError.SettingsError(error_msg)
