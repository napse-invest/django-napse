from django.db import models

from django_napse.core.models.connections.managers import ConnectionManager
from django_napse.utils.usefull_functions import process_value_from_type


class Connection(models.Model):
    space = models.ForeignKey("NapseSpace", on_delete=models.CASCADE, related_name="connections")
    bot = models.ForeignKey("Bot", on_delete=models.CASCADE, related_name="connections")
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    objects = ConnectionManager()

    class Meta:
        unique_together = ("space", "bot")

    def __str__(self):  # pragma: no cover
        return f"CONNECTION: {self.pk=}, {self.bot.name=}, {self.space.name=}"


class ConnectionSpecificArgs(models.Model):
    connection = models.ForeignKey("Connection", on_delete=models.CASCADE, related_name="specific_args")
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100, default="None")
    target_type = models.CharField(max_length=100, default="None")

    class Meta:
        unique_together = ("connection", "key")

    def __str__(self):  # pragma: no cover
        string = f"CONNECTION_SPECIFIC_ARGS: {self.pk=},"
        return string + f"connection__pk={self.connection.pk}, key={self.key}, value={self.value}, target_type={self.target_type}"
