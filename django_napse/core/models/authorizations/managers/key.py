import secrets

from django.db import models

from django_napse.utils.errors import NapseError


class NapseAPIKeyManager(models.Manager):
    def create(self, name, description):
        attempts = 0
        while attempts < 10:
            attempts += 1
            napse_API_key = secrets.token_urlsafe(64)
            if not self.filter(napse_API_key=napse_API_key).exists():
                break
        else:
            error_msg = f"Unable to generate a unique API key for the space {name}"
            raise NapseError.NapseRandomGenrationError(error_msg)
        return super().create(name=name, description=description, napse_API_key=napse_API_key)
