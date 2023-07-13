from django.db import models


class PermissionType(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return f"PERMISSION TYPE: {self.name}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Permission Type ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.name=}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string


class KeyPermission(models.Model):
    key = models.ForeignKey("NapseAPIKey", on_delete=models.CASCADE, related_name="permissions")
    space = models.ForeignKey("NapseSpace", on_delete=models.CASCADE)
    permission_type = models.ForeignKey("PermissionType", on_delete=models.CASCADE)

    def __str__(self):
        return f"NAPSE KEY PERMISSION: {self.permission_type.name} - {self.key.name} - {self.exchange_account.exchange.name}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Napse Key Permission ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.key=}\n"
        string += f"{beacon}\t{self.space}\n"
        string += f"{beacon}\t{self.permission_type}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string
