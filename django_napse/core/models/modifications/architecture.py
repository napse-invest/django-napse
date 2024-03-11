from django.db import models

from django_napse.utils.constants import MODIFICATION_STATUS
from django_napse.utils.usefull_functions import process_value_from_type

from .modification import Modification


class ArchitectureModification(Modification):
    def apply(self):
        architecture = self.order.connection.bot.architecture.find()
        architectur, self = self.apply__no_db(architecture)
        architecture.save()
        self.save()

    def apply__no_db(self, **kwargs: dict) -> tuple[models.Model, "ArchitectureModification"]:
        architecture = kwargs.get("architecture")
        if not hasattr(architecture, f"variable_{self.key}"):
            error_msg: str = f"Architecture {architecture} must have attribute {self.key}"
            raise ValueError(error_msg)

        setattr(architecture, f"variable_{self.key}", process_value_from_type(self.value, self.target_type))
        self.status = MODIFICATION_STATUS.APPLIED
        return architecture, self
