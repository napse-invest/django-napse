from django.db import models

from django_napse.core.models.transactions.managers import TransactionManager
from django_napse.utils.constants import TRANSACTION_TYPES


class Transaction(models.Model):
    """A Transaction is a transfer of value between two wallets."""

    from_wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE, related_name="transactions_from")
    to_wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE, related_name="transactions_to")
    amount = models.FloatField()
    ticker = models.CharField(max_length=10)
    transaction_type = models.CharField(max_length=20, default=TRANSACTION_TYPES.TRANSFER)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TransactionManager()

    def __str__(self) -> str:
        return f"TRANSACTION: {self.from_wallet.pk} -> {self.to_wallet.pk} ({self.amount=} - {self.ticker=})"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}Transaction {self.pk=}\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.amount=}\n"
        string += f"{beacon}\t{self.ticker=}\n"
        string += f"{beacon}\t{self.transaction_type=}\n"
        string += f"{beacon}From Wallet:\n"
        wall_str = self.from_wallet.info(verbose=False, beacon=beacon + "\t")
        string += f"{wall_str}\n"
        string += f"{beacon}To Wallet:\n"
        wall_str = self.to_wallet.info(verbose=False, beacon=beacon + "\t")
        string += f"{wall_str}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string
