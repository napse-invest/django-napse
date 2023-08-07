# MANAGERS
from django.db import models

from django_napse.core.models.orders.managers import OrderManager
from django_napse.utils.constants import ORDER_STATUS
from django_napse.utils.errors import OrderError


class Order(models.Model):
    connection = models.ForeignKey("Connection", on_delete=models.CASCADE, related_name="orders")
    amount = models.FloatField()
    price = models.FloatField()
    pair = models.CharField(max_length=10)
    side = models.CharField(max_length=10)
    status = models.CharField(default=ORDER_STATUS.PENDING, max_length=15)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OrderManager()

    def __str__(self):
        return f"ORDER: {self.connection} {self.status=}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Order ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.connection=}\n"
        string += f"{beacon}\t{self.pair=}\n"
        string += f"{beacon}\t{self.amount=}\n"
        string += f"{beacon}\t{self.side=}\n"
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
    def testing(self):
        return self.connection.testing

    @property
    def exchange_account(self):
        return self.connection.wallet.exchange_account

    def set_status_ready(self):
        if self.status == ORDER_STATUS.PENDING:
            self.status = ORDER_STATUS.READY
            self.save()
        else:
            error_msg: str = f"Order {self.pk} is not pending."
            raise OrderError.StatusError(error_msg)

    def set_status_passed(self):
        if self.status == ORDER_STATUS.PENDING:
            self.status = ORDER_STATUS.PASSED
            self.save()
        else:
            error_msg: str = f"Order {self.pk} is not pending."
            raise OrderError.StatusError(error_msg)

    def set_status_failed(self):
        if self.status == ORDER_STATUS.PENDING:
            self.status = ORDER_STATUS.FAILED
            self.save()
        else:
            error_msg: str = f"Order {self.pk} is not pending."
            raise OrderError.StatusError(error_msg)
