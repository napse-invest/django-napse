from django.db import models

from django_napse.core.models.bots.architechture import Architechture


class SinglePairArchitechture(Architechture):
    controller = models.ForeignKey("Controller", on_delete=models.CASCADE, related_name="single_pair_architechtures")

    def __str__(self) -> str:
        return f"SinglePairArchitechture {self.pk} ({self.pair=})"
