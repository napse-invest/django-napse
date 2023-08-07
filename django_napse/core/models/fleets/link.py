from django.db import models


class Link(models.Model):
    bot = models.OneToOneField("Bot", on_delete=models.CASCADE, related_name="link")
    cluster = models.ForeignKey("Cluster", on_delete=models.CASCADE, related_name="links")

    def __str__(self):
        return f"LINK: {self.bot} {self.fleet}"
