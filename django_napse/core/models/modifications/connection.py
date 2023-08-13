from django.db import models

from django_napse.utils.constants import MODIFICATION_STATUS

from .modification import Modification


class ConnectionModification(Modification):
    connection_specific_arg = models.ForeignKey("ConnectionSpecificArgs", on_delete=models.CASCADE, related_name="modifications")

    def apply(self):
        connection_specific_arg, self = self._apply()
        connection_specific_arg.save()
        self.save()

    def _apply(self, **kwargs):
        self.connection_specific_arg.value = self.get_value(current_value=self.connection_specific_arg.get_value(), **kwargs)
        self.status = MODIFICATION_STATUS.APPLIED
        return self.connection_specific_arg, self
