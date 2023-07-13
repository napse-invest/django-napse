# MANAGERS
from django.db import models

from django_napse.core.models.orders.managers import OrderManager
from django_napse.utils.constants import ORDER_STATUS
from django_napse.utils.errors import OrderError


class Order(models.Model):
    bot = models.ForeignKey("Bot", on_delete=models.CASCADE, related_name="orders")
    buy_amount = models.FloatField()
    sell_amount = models.FloatField()
    price = models.FloatField()
    status = models.CharField(default=ORDER_STATUS.PENDING, max_length=15)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OrderManager()

    def __str__(self):
        return f"ORDER: {self.bot} {self.status=}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Transaction ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.bot=}\n"
        string += f"{beacon}\t{self.pair=}\n"
        string += f"{beacon}\t{self.buy_amount=}\n"
        string += f"{beacon}\t{self.sell_amount=}\n"
        string += f"{beacon}\t{self.price=}\n"
        string += f"{beacon}\t{self.status=}\n"
        string += f"{beacon}\t{self.completed=}\n"

        new_beacon = beacon + "\t"
        string += f"{beacon}Wallet:\n"
        string += f"{beacon}{self.wallet.info(verbose=False, beacon=new_beacon)}\n"
        string += f"{beacon}Transactions in:\n"
        if self.wallet.transactions_to.all().count() == 0:
            string += f"{beacon}\tNone.\n"
        else:
            for transaction in self.wallet.transactions_to.all():
                trans_str = transaction.info(verbose=False, beacon=new_beacon)
                string += f"{trans_str}\n"
        string += f"{beacon}Transactions out:\n"
        if self.wallet.transactions_from.all().count() == 0:
            string += f"{beacon}\tNone.\n"
        else:
            for transaction in self.wallet.transactions_from.all():
                trans_str = transaction.info(verbose=False, beacon=new_beacon)
                string += f"{trans_str}\n"
        if verbose:  # pragma: no cover
            print(string)
        return string

    @property
    def pair(self):
        return self.bot.pair

    @property
    def testing(self):
        return self.bot.testing

    @property
    def space(self):
        return self.bot.space

    def set_status_passed(self):
        if self.status == ORDER_STATUS.PENDING:
            self.status = ORDER_STATUS.PASSED
            super().save()
        else:
            error_msg: str = f"Order {self.pk} is not pending."
            raise OrderError.StatusError(error_msg)

    def set_status_failed(self):
        if self.status == ORDER_STATUS.PENDING:
            self.status = ORDER_STATUS.FAILED
            super().save()
        else:
            error_msg: str = f"Order {self.pk} is not pending."
            raise OrderError.StatusError(error_msg)

    def set_status_only_sell_passed(self):
        if self.status == ORDER_STATUS.PENDING:
            self.status = ORDER_STATUS.ONLY_SELL_PASSED
            super().save()
        else:
            error_msg: str = f"Order {self.pk} is not pending."
            raise OrderError.StatusError(error_msg)

    def set_status_only_sell(self):
        if self.status == ORDER_STATUS.PENDING:
            self.status = ORDER_STATUS.ONLY_SELL_PASSED
            super().save()
        else:
            error_msg: str = f"Order {self.pk} is not pending."
            raise OrderError.StatusError(error_msg)
