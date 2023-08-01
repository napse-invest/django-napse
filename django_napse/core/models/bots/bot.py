import uuid

from django.db import models

from django_napse.utils.errors import BotError


class Bot(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    name = models.CharField(max_length=100, default="Bot")

    can_trade = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    strategy = models.ForeignKey("Strategy", on_delete=models.CASCADE, related_name="bots")

    def __str__(self):
        return f"BOT {self.name=} ({self.pair=})"

    def info(self, verbose=True, beacon=""):  # pragma: no cover
        string = ""
        string += f"{beacon}Bot {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.__class__=}\n"
        string += f"{beacon}\t{self.base=}\n"
        string += f"{beacon}\t{self.quote=}\n"
        string += f"{beacon}\t{self.interval=}\n"
        string += f"{beacon}\t{self.testing=}\n"
        string += f"{beacon}\t{self.is_in_simulation=}\n"
        string += f"{beacon}\t{self.can_trade=}\n"

        for arg in self.specific_args:
            string += f"{beacon}\t{arg}={getattr(self, arg)}\n"

        # string += f"{beacon}Connections:\n"
        # if self.get_owners().count() == 0:
        #     string += f"{beacon}\tNone\n"
        # else:
        #     for connection in self.get_owners():
        #         conn_str = connection.info(verbose=False, beacon=beacon + "\t")
        #         string += f"{conn_str}\n"
        if verbose:
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

    def validate_settings(self):
        pass

    def validate_variables(self, **kwargs):
        pass

    def get_connections(self):
        return list(self.connections.all())

    def trigger_actions(self):
        connections = self.get_connections()
        orders, modifictions = self.architechture.find().trigger_actions(bot=self, connections=connections)
        for order in orders:
            order.set_status_ready()
        for modification in modifictions:
            modification.save()
