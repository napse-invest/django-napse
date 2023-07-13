from django.db import models

from django_napse.utils.errors import ClusterError


class Cluster(models.Model):
    fleet = models.ForeignKey("Fleet", on_delete=models.CASCADE, related_name="clusters")
    config = models.OneToOneField("BotConfig", on_delete=models.CASCADE, related_name="clusters")

    def __str__(self):
        return f"CLUSTER: {self.bot} {self.fleet} {self.config}"

    def save(self, *args, **kwargs):
        if not self.config.immutable:
            error_msg = f"Config {self.config} is not immutable."
            raise ClusterError.MutableBotConfig(error_msg)
        super().save(*args, **kwargs)

    def deploy(self):
        if self.bots.count() > 0:
            error_msg = f"Cluster {self} is not empty."
            raise ClusterError.NotEmpty(error_msg)
        bot = self.config.to_bot()
        BotInCluster.objects.create(bot=bot, cluster=self)


class BotInCluster(models.Model):
    bot = models.OneToOneField("Bot", on_delete=models.CASCADE, related_name="bot_in_cluster")
    cluster = models.ForeignKey("Cluster", on_delete=models.CASCADE, related_name="bots")

    def __str__(self):
        return f"BOT IN CLUSTER: {self.bot} {self.cluster}"
