import uuid

from django.db import models

from django_napse.utils.errors import BotError


class Bot(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    name = models.CharField(max_length=100, default="Bot")

    can_trade = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    strategy = models.OneToOneField("Strategy", on_delete=models.CASCADE, related_name="bot")

    def __str__(self):
        return f"BOT {self.pk=}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Bot {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.name=}\n"
        string += f"{beacon}\t{self.can_trade=}\n"

        string += f"{beacon}Strategy:\n"
        new_beacon = beacon + "\t"
        string += f"{beacon}\t{self.strategy.info(verbose=False, beacon=new_beacon)}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def is_in_simulation(self):
        return hasattr(self, "simulation")

    @property
    def is_in_fleet(self):
        return hasattr(self, "bot_in_cluster")

    @property
    def testing(self):
        if self.is_in_simulation:
            return True
        if self.is_in_fleet:
            return self.bot_in_cluster.cluster.fleet.testing
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    @property
    def space(self):
        if self.is_in_simulation:
            return self.simulation.space
        if self.is_in_fleet:
            error_msg = "Bot is in a fleet and therefore doesn't have a space."
            raise BotError.NoSpace(error_msg)
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    @property
    def exchange_account(self):
        if self.is_in_simulation:
            return self.simulation.space.exchange_account
        if self.is_in_fleet:
            return self.bot_in_cluster.cluster.fleet.exchange_account
        error_msg = "Bot is not in simulation or fleet."
        raise BotError.InvalidSetting(error_msg)

    @property
    def _strategy(self):
        return self.strategy.find()

    @property
    def architechture(self):
        return self._strategy.architechture.find()

    def get_connections(self):
        return list(self.connections.all())

    def trigger_actions(self):
        connections = self.get_connections()
        orders, modifictions = self.architechture.trigger_actions(bot=self, data=self.architechture.prepare_data(), connections=connections)
        for order in orders:
            order.set_status_ready()
        for modification in modifictions:
            modification.save()
