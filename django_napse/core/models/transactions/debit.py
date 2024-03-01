from django.db import models

from django_napse.core.models.transactions.managers import DebitManager


class Debit(models.Model):
    """A Debit is a transaction that forcefully removes money from a wallet."""

    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE, related_name="debits")
    amount = models.FloatField()
    ticker = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DebitManager()

    def __str__(self) -> str:  # pragma: no cover
        return f"DEBIT: {self.pk})"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}Debit {self.pk=}\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.amount=}\n"
        string += f"{beacon}\t{self.ticker=}\n"
        string += f"{beacon}Debited Wallet:\n"
        wall_str = self.wallet.info(verbose=False, beacon=beacon + "\t")
        string += f"{wall_str}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string
