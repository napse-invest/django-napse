from django.db import models
from django.db.transaction import atomic


class CreditManager(models.Manager):
    @atomic()
    def create(self, wallet, amount, ticker):
        if amount == 0:
            return None
        credit = self.model(
            wallet=wallet,
            amount=amount,
            ticker=ticker,
        )

        credit.save()
        wallet.top_up(amount, ticker, force=True)
        return credit
