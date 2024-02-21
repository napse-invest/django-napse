from django.db import models


class Link(models.Model):
    bot = models.OneToOneField("Bot", on_delete=models.CASCADE, related_name="link")
    cluster = models.ForeignKey("Cluster", on_delete=models.CASCADE, related_name="links")
    importance = models.FloatField()

    def __str__(self):
        return f"LINK: {self.bot=} {self.cluster=}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Link {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.bot=}\n"
        string += f"{beacon}\t{self.cluster=}\n"
        string += f"{beacon}\t{self.importance=}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string
