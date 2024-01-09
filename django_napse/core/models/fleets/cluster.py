from django.db import models

# from django_napse.core.models.connections.connection import Connection
from django_napse.core.models.fleets.link import Link
from django_napse.core.models.transactions.transaction import Transaction
from django_napse.utils.constants import TRANSACTION_TYPES
from django_napse.utils.errors import BotError, ClusterError


class Cluster(models.Model):
    fleet = models.ForeignKey(
        "Fleet",
        on_delete=models.CASCADE,
        related_name="clusters",
    )
    template_bot = models.OneToOneField(
        "Bot",
        on_delete=models.CASCADE,
        related_name="cluster",
    )
    share = models.FloatField()
    breakpoint = models.FloatField()
    autoscale = models.BooleanField()

    def __str__(self):
        return f"Cluster: {self.fleet}"

    def save(self, *args, **kwargs):
        if not self.config.immutable:
            error_msg = "In a fleet, the config must be immutable."
            raise ClusterError.MutableBotConfig(error_msg)
        return super().save(*args, **kwargs)

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Cluster {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.fleet=}\n"
        string += f"{beacon}\t{self.template_bot=}\n"
        string += f"{beacon}\t{self.share=}\n"
        string += f"{beacon}\t{self.breakpoint=}\n"
        string += f"{beacon}\t{self.autoscale=}\n"

        new_beacon = beacon + "\t"
        string += f"{beacon}Links:\n"
        for link in self.links.all():
            string += f"{link.info(verbose=False, beacon=new_beacon)}\n"

        string += f"{beacon}Connections:\n"
        connections = []
        for link in self.links.all():
            connections += list(link.bot.connections.all())
        for connection in connections:
            string += f"{connection.info(verbose=False, beacon=new_beacon)}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def config(self):
        return self.template_bot.strategy.config

    def invest(self, space, amount, ticker):
        all_connections = []
        bots = [link.bot for link in self.links.all().order_by("importance")]
        if len(bots) == 0:
            new_bot = self.template_bot.copy()
            Link.objects.create(bot=new_bot, cluster=self, importance=1)
            # connection = Connection.objects.create(bot=new_bot, owner=space.wallet)
            connection = space.wallet.connect_to_bot(new_bot)
            Transaction.objects.create(
                from_wallet=space.wallet,
                to_wallet=connection.wallet,
                amount=amount,
                ticker=ticker,
                transaction_type=TRANSACTION_TYPES.CONNECTION_DEPOSIT,
            )
            all_connections.append(connection)
        elif len(bots) == 1:
            bot = bots[0]
            if ticker not in bot.architecture.accepted_investment_tickers() or ticker not in bot.architecture.accepted_tickers():
                error_msg = f"Bot {bot} does not accept ticker {ticker}."
                raise BotError.InvalidTicker(error_msg)

            connection = space.wallet.connect_to_bot(bot)
            # connection = Connection.objects.get(bot=bot, owner=space.wallet)
            Transaction.objects.create(
                from_wallet=space.wallet,
                to_wallet=connection.wallet,
                amount=amount,
                ticker=ticker,
                transaction_type=TRANSACTION_TYPES.CONNECTION_DEPOSIT,
            )
            all_connections.append(connection)
        else:
            error_msg = "Autoscale not implemented yet."
            raise NotImplementedError(error_msg)
        return all_connections
