from django.db import models

from django_napse.utils.constants import PERMISSION_TYPES


class KeyPermission(models.Model):
    key = models.ForeignKey("NapseAPIKey", on_delete=models.CASCADE, related_name="permissions")
    space = models.ForeignKey("django_napse_core.NapseSpace", on_delete=models.CASCADE)
    valid = models.BooleanField(default=True)
    permission_type = models.CharField(max_length=200)

    def __str__(self):
        return f"NAPSE KEY PERMISSION: {self.permission_type.name} - {self.key.name} - {self.exchange_account.exchange.name}"

    def save(self, *args, **kwargs):
        if self.permission_type not in PERMISSION_TYPES:
            error_msg = f"Permission type ({self.permission_type}) is not valid. Valid permission types are: {PERMISSION_TYPES}"
            raise ValueError(error_msg)
        super().save(*args, **kwargs)

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Napse Key Permission ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.key=}\n"
        string += f"{beacon}\t{self.space=}\n"
        string += f"{beacon}\t{self.permission_type=}\n"
        string += f"{beacon}\t{self.valid=}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string
