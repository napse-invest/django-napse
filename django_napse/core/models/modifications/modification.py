from django.db import models

from django_napse.utils.constants import MODIFICATION_STATUS
from django_napse.utils.findable_class import FindableClass
from django_napse.utils.usefull_functions import process_value_from_type


class Modification(models.Model, FindableClass):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="modifications")

    status = models.CharField(default=MODIFICATION_STATUS.PENDING, max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    ignore_failed_order = models.BooleanField(default=False)

    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"MODIFICATION: {self.pk=}"

    def get_value(self, **kwargs):
        return process_value_from_type(self.value, self.target_type, **kwargs)
