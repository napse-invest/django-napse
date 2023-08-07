from django.db import models

from django_napse.core.models.transactions.managers import DebitManager


class Debit(models.Model):
    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE, related_name="debits")
    amount = models.FloatField()
    ticker = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DebitManager()

    def __str__(self):
        return f"DEBIT: {self.pk})"

    def info(self, verbose=True, beacon=""):
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
