from typing import TYPE_CHECKING

from django.db import models

from django_napse.core.models.connections.managers import ConnectionManager
from django_napse.core.models.transactions.transaction import Transaction
from django_napse.utils.constants import TRANSACTION_TYPES
from django_napse.utils.usefull_functions import process_value_from_type

if TYPE_CHECKING:
    from django_napse.core.models.accounts.space import Space


class Connection(models.Model):
    """Link between a bot & a wallet."""

    owner = models.ForeignKey("Wallet", on_delete=models.CASCADE, related_name="connections")
    bot = models.ForeignKey("Bot", on_delete=models.CASCADE, related_name="connections")

    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    objects = ConnectionManager()

    class Meta:  # noqa: D106
        unique_together = ("owner", "bot")

    def __str__(self) -> str:  # pragma: no cover
        return f"CONNECTION: {self.pk=}"

    def info(self, verbose: bool = True, beacon: str = "") -> str:  # noqa: FBT001, FBT002
        """Give info on the Connection instance."""
        string = ""
        string += f"{beacon}Connection {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.owner=}\n"
        string += f"{beacon}\t{self.bot=}\n"
        string += f"{beacon}\t{self.created_at=}\n"

        string += f"{beacon}Wallet:\n"
        new_beacon = beacon + "\t"
        string += f"{self.wallet.info(verbose=False, beacon=new_beacon)}\n"

        string += f"{beacon}ConnectionSpecificArgs:\n"
        query = self.specific_args.all()
        if query.count() == 0:
            string += f"{beacon}\tNone\n"
        else:
            for connection_specific_arg in query:
                string += f"{connection_specific_arg.info(verbose=False, beacon=new_beacon)}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def testing(self) -> bool:
        """Return true if the connection's space is in testing."""
        return self.space.testing

    @property
    def space(self) -> "Space":
        """Return the space of the connection."""
        return self.owner.find().space

    def deposit(self, ticker: str, amount: int) -> Transaction:
        """Make a transaction from owner's wallet to bot's wallet."""
        return Transaction.objects.create(
            from_wallet=self.owner,
            to_wallet=self.wallet,
            amount=amount,
            ticker=ticker,
            transaction_type=TRANSACTION_TYPES.CONNECTION_DEPOSIT,
        )

    def withdraw(self, ticker: str, amount: int) -> Transaction:
        """Make a transaction from bot's wallet to owner's wallet."""
        return Transaction.objects.create(
            from_wallet=self.wallet,
            to_wallet=self.owner,
            amount=amount,
            ticker=ticker,
            transaction_type=TRANSACTION_TYPES.CONNECTION_WITHDRAW,
        )

    def to_dict(self) -> dict[str, any]:
        """Return a connection to a dictionary."""
        return {
            "connection": self,
            "wallet": self.wallet.find().to_dict(),
            "connection_specific_args": {arg.key: arg for arg in self.specific_args.all()},
        }


class ConnectionSpecificArgs(models.Model):
    """Argument of a connection.

    A connection can have a infinite number of arguments.
    """

    connection = models.ForeignKey("Connection", on_delete=models.CASCADE, related_name="specific_args")
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100, default="None")
    target_type = models.CharField(max_length=100, default="None")

    class Meta:  # noqa: D106
        unique_together = ("connection", "key")

    def __str__(self) -> str:  # pragma: no cover
        string = f"CONNECTION_SPECIFIC_ARGS: {self.pk=},"
        return string + f"connection__pk={self.connection.pk}, key={self.key}, value={self.value}, target_type={self.target_type}"

    def info(self, verbose: bool = True, beacon: str = "") -> str:  # noqa: FBT001, FBT002
        """Give info on the ConnectionSpecificArgs instance."""
        string = ""
        string += f"{beacon}ConnectionSpecificArgs {self.pk}:\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.connection=}\n"
        string += f"{beacon}\t{self.key=}\n"
        string += f"{beacon}\t{self.value=}\n"
        string += f"{beacon}\t{self.target_type=}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string

    def get_value(self) -> any:
        """Return the value in the correct type."""
        return process_value_from_type(self.value, self.target_type)
