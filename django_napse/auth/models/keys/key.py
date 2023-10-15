import contextlib

from django.db import IntegrityError, models
from rest_framework_api_key.models import APIKey

from django_napse.auth.models.permissions import KeyPermission
from django_napse.utils.errors import NapseKeyError


class NapseAPIKey(APIKey):
    is_master_key = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs) -> None:
        if self.is_master_key:
            self.name = "Napse Master Key"
        if self.is_master_key and NapseAPIKey.objects.filter(is_master_key=True).count() > (1 if self.pk else 0):
            error_msg = "Only one master key can exist at a time."
            raise NapseKeyError.DuplicateMasterkey(error_msg)
        return super().save(*args, **kwargs)

    def add_permission(self, space, permission):
        with contextlib.suppress(IntegrityError):
            KeyPermission.objects.create(key=self, space=space, permission_type=permission)

    def revoke(self):
        self.revoked = True
        self.save()
