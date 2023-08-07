from django.db import models

from django_napse.core.models.authorizations.managers import NapseAPIKeyManager


class NapseAPIKey(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    napse_API_key = models.CharField(max_length=200, unique=True)

    objects = NapseAPIKeyManager()

    def __str__(self):
        return f"NAPSE API KEY: {self.name}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Napse API Key ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.name=}\n"
        new_beacon = beacon + "\t"
        for permission in self.permissions.all():
            string += f"{permission.info(verbose=False, beacon=new_beacon)}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string
