from django.db import models

from .account import NapseAccount


class Exchange(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return f"EXCHANGE: {self.name}"


class ExchangeAccount(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    napse_account = models.OneToOneField(NapseAccount, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EXCHANGE ACCOUNT: {self.exchange.name=} - {self.napse_account.name=}"

    def ping(self):
        error_msg = f"ping() not implemented for {self.__class__.__name__}"
        raise NotImplementedError(error_msg)


class BinanceAccount(ExchangeAccount):
    public_key = models.CharField(max_length=200)
    private_key = models.CharField(max_length=200)

    class Meta:
        unique_together = ("public_key", "private_key")


EXCHANGE_ACCOUNT_DICT = {
    "BINANCE": BinanceAccount,
}
