from django.db import models


class Modification(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="modifications")

    applied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    ignore_failed_order = models.BooleanField(default=False)

    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"MODIFICATION: {self.pk=}"
