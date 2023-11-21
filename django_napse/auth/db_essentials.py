import contextlib
import json

from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from django_napse.core.settings import napse_settings
from django_napse.utils.errors import NapseKeyError


@receiver(post_migrate)
def create_master_key(sender, **kwargs):
    NapseAPIKey = apps.get_model("django_napse_auth", "NapseAPIKey")
    with contextlib.suppress(NapseKeyError.DuplicateMasterkey):
        _, key = NapseAPIKey.objects.create_key(name="", is_master_key=True)
        print(f"Master key created: {key}")
        with open(napse_settings.NAPSE_SECRETS_FILE_PATH, "r") as f:
            secrets = json.load(f)
            secrets["master_key"] = key
        with open(napse_settings.NAPSE_SECRETS_FILE_PATH, "w") as f:
            json.dump(secrets, f, indent=4)
