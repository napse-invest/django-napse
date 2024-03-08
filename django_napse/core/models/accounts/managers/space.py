from django.apps import apps
from django.db import models


class SpaceManager(models.Manager):
    def create(self, name: str, exchange_account, description: str = ""):
        """Create a Space instance."""
        SpaceWallet = apps.get_model("django_napse_core", "SpaceWallet")
        SpaceSimulationWallet = apps.get_model("django_napse_core", "SpaceSimulationWallet")

        space = self.model(
            name=name,
            exchange_account=exchange_account,
            description=description,
        )
        space.save()

        SpaceWallet.objects.create(owner=space, title=f"Wallet for space {space.name}")
        SpaceSimulationWallet.objects.create(owner=space, title=f"Simulation Wallet for space {space.name}")

        return space
