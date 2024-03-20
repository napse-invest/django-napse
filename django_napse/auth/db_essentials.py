import contextlib
import json
from pathlib import Path

from django.apps import AppConfig, apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from django_napse.core.settings import napse_settings
from django_napse.utils.errors import NapseKeyError


@receiver(post_migrate)
def create_master_key(sender: AppConfig, **kwargs: dict) -> None:  # noqa: ARG001
    """Create a master key for the Napse API."""
    NapseAPIKey = apps.get_model("django_napse_auth", "NapseAPIKey")
    with contextlib.suppress(NapseKeyError.DuplicateMasterkey):
        _, key = NapseAPIKey.objects.create_key(name="", is_master_key=True)

        Path.mkdir(Path(Path.home() / ".napse-dev"), exist_ok=True)
        with Path(Path.home() / ".napse-dev" / "api-keys.json").open("w") as f:
            json.dump({"Django Napse Dev": {"url": "http://localhost:8000", "token": key}}, f, indent=4)
        with Path(napse_settings.NAPSE_SECRETS_FILE_PATH).open("r") as f:
            secrets = json.load(f)
            secrets["master_key"] = key
        with Path(napse_settings.NAPSE_SECRETS_FILE_PATH).open("w") as f:
            json.dump(secrets, f, indent=4)
