from django.db import models

from .modification import Modification


class ConnectionModification(Modification):
    connection_specific_arg = models.ForeignKey("ConnectionSpecificArgs", on_delete=models.CASCADE, related_name="modifications")

    def apply(self):
        self._apply(None)
        self.connection_specific_arg.save()
        self.save()

    def _apply(self, **kwargs):
        self.connection_specific_arg.value = self.value
        self.applied = True
