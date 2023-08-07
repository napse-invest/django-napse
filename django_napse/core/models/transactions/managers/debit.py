from django.db import models
from django.db.transaction import atomic


class DebitManager(models.Manager):
    @atomic()
    def create(self, wallet, amount, ticker):
        if amount == 0:
            return None
        debit = self.model(
            wallet=wallet,
            amount=amount,
            ticker=ticker,
        )

        debit.save()
        wallet.spend(amount, ticker, force=True)
        return debit
