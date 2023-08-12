from django.db import models

from django_napse.utils.constants import MODIFICATION_STATUS

from .modification import Modification


class ConnectionModification(Modification):
    connection_specific_arg = models.ForeignKey("ConnectionSpecificArgs", on_delete=models.CASCADE, related_name="modifications")

    def apply(self):
        self._apply(None)
        self.connection_specific_arg.save()
        self.save()

    def _apply(self, **kwargs):
        self.connection_specific_arg.value = self.value
        self.status = MODIFICATION_STATUS.APPLIED
