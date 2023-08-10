from django.db import models

from django_napse.core.models.connections.managers import ConnectionManager
from django_napse.core.models.transactions.transaction import Transaction
from django_napse.utils.constants import TRANSACTION_TYPES


class Connection(models.Model):
    owner = models.ForeignKey("Wallet", on_delete=models.CASCADE, related_name="connections")
    bot = models.ForeignKey("Bot", on_delete=models.CASCADE, related_name="connections")

    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    objects = ConnectionManager()

    class Meta:
        unique_together = ("owner", "bot")

    def __str__(self):  # pragma: no cover
        return f"CONNECTION: {self.pk=}"

    @property
    def testing(self):
        return self.wallet.space.testing

    @property
    def space(self):
        return self.owner.space

    def deposit(self, ticker, amount):
        return Transaction.objects.create(
            from_wallet=self.owner,
            to_wallet=self.wallet,
            amount=amount,
            ticker=ticker,
            transaction_type=TRANSACTION_TYPES.CONNECTION_DEPOSIT,
        )

    def withdraw(self, ticker, amount):
        return Transaction.objects.create(
            from_wallet=self.wallet,
            to_wallet=self.owner,
            amount=amount,
            ticker=ticker,
            transaction_type=TRANSACTION_TYPES.CONNECTION_WITHDRAW,
        )


class ConnectionSpecificArgs(models.Model):
    connection = models.ForeignKey("Connection", on_delete=models.CASCADE, related_name="specific_args")
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100, default="None")
    target_type = models.CharField(max_length=100, default="None")

    class Meta:
        unique_together = ("connection", "key")

    def __str__(self):  # pragma: no cover
        string = f"CONNECTION_SPECIFIC_ARGS: {self.pk=},"
        return string + f"connection__pk={self.connection.pk}, key={self.key}, value={self.value}, target_type={self.target_type}"
