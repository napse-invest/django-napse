import shortuuid
from django.apps import apps
from django.db import models

from django_napse.utils.errors import NapseError


class NapseSpaceManager(models.Manager):
    def create(self, name: str, exchange_account, description: str = ""):
        SpaceWallet = apps.get_model("django_napse_core", "SpaceWallet")
        SpaceSimulationWallet = apps.get_model("django_napse_core", "SpaceSimulationWallet")
        attempts = 0
        while attempts < 10:
            attempts += 1
            uuid = shortuuid.ShortUUID(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789").random(length=5)
            if not self.filter(identifier=f"#{uuid}").exists():
                break
        else:
            error_msg = f"Unable to generate a unique identifier for the space {name}"
            raise NapseError.RandomGenrationError(error_msg)
        space = self.model(
            name=name,
            exchange_account=exchange_account,
            identifier=f"#{uuid}",
            description=description,
        )
        space.save()

        SpaceWallet.objects.create(owner=space, title=f"Wallet for space {space.name}")
        SpaceSimulationWallet.objects.create(owner=space, title=f"Simulation Wallet for space {space.name}")

        return space
