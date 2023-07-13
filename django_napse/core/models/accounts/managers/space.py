import shortuuid
from django.db import models

from django_napse.utils.errors import NapseError


class NapseSpaceManager(models.Manager):
    def create(self, name: str, exchange_account, description: str = ""):
        attempts = 0
        while attempts < 10:
            attempts += 1
            uuid = shortuuid.ShortUUID(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789").random(length=5)
            if not self.filter(name=name, identifier=f"#{uuid}").exists():
                break
        else:
            error_msg = f"Unable to generate a unique identifier for the space {name}"
            raise NapseError.RandomGenrationError(error_msg)
        return super().create(
            name=name,
            exchange_account=exchange_account,
            identifier=f"#{uuid}",
            description=description,
        )
