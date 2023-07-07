from django.db import models


class NapseAccount(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    napse_API_key = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f"ACCOUNT: {self.name}"
