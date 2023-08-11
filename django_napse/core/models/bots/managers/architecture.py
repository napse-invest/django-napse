from typing import Optional

from django.db import models


class ArchitectureManager(models.Manager):
    def create(self, constants: Optional[dict] = None, variables: Optional[dict] = None) -> models.Model:
        constants = constants or {}
        variables = variables or {}
        architecture = self.model(**constants, **{f"variable_{key}": value for key, value in variables.items()})
        architecture.save()
        return architecture
