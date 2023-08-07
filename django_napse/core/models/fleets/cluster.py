from django.db import models

from django_napse.utils.errors import ClusterError


class Cluster(models.Model):
    fleet = models.ForeignKey("Fleet", on_delete=models.CASCADE, related_name="clusters")

    def __str__(self):
        return f"Cluster: {self.fleet}"

    def save(self, *args, **kwargs):
        configs = [link.bot.strategy.config for link in self.links.all()]
        if len(set(configs)) != 1:
            error_msg = "All bots in a cluster must have the same config."
            raise ClusterError.MultipleConfigs(error_msg)
        if not configs[0].immutable:
            error_msg = "The config must be immutable."
            raise ClusterError.MutableBotConfig(error_msg)
        return super().save(*args, **kwargs)

    @property
    def config(self):
        return self.links.first().bot.strategy.config
