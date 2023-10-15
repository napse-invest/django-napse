import contextlib

from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from django_napse.utils.errors import NapseKeyError


@receiver(post_migrate)
def create_master_key(sender, **kwargs):
    NapseAPIKey = apps.get_model("django_napse_auth", "NapseAPIKey")
    with contextlib.suppress(NapseKeyError.DuplicateMasterkey):
        _, key = NapseAPIKey.objects.create_key(name="", is_master_key=True)
        print(f"Master key created: {key}")
