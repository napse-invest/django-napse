from django.db import models

from django_napse.core.models.orders.managers import OrderManager
from django_napse.utils.constants import ORDER_STATUS, SIDES
from django_napse.utils.errors import OrderError


class OrderBatch(models.Model):
    status = models.CharField(default=ORDER_STATUS.PENDING, max_length=15)
    controller = models.ForeignKey("Controller", on_delete=models.CASCADE, related_name="order_batches")

    def __str__(self) -> str:
        return f"ORDER BATCH {self.pk}"

    def set_status_ready(self):
        if self.status == ORDER_STATUS.PENDING:
            self.status = ORDER_STATUS.READY
            self.save()
        else:
            error_msg = f"Order {self.pk} is not pending."
            raise OrderError.StatusError(error_msg)

    def set_status_post_process(self, executed_amounts_buy: dict, executed_amounts_sell: dict, save: bool) -> None:
        if self.status != ORDER_STATUS.READY:
            error_msg = f"Order {self.pk} is not ready."
            raise OrderError.StatusError(error_msg)
        buy_failed = False
        sell_failed = False
        if "error" in executed_amounts_buy:
            buy_failed = True
        if "error" in executed_amounts_sell:
            sell_failed = True
        if buy_failed and sell_failed:
            self.status = ORDER_STATUS.FAILED
        elif buy_failed:
            self.status = ORDER_STATUS.ONLY_SELL_PASSED
        elif sell_failed:
            self.status = ORDER_STATUS.ONLY_BUY_PASSED
        else:
            self.status = ORDER_STATUS.PASSED
        if save:
            self.save()


class Order(models.Model):
    batch = models.ForeignKey("OrderBatch", on_delete=models.CASCADE, related_name="orders")
    connection = models.ForeignKey("Connection", on_delete=models.CASCADE, related_name="orders")
    price = models.FloatField()
    pair = models.CharField(max_length=10)
    side = models.CharField(max_length=10)
    completed = models.BooleanField(default=False)

    asked_for_amount = models.FloatField()
    asked_for_ticker = models.CharField(max_length=10)

    debited_amount = models.FloatField(default=0)

    batch_share = models.FloatField(default=0)
    exit_base_amount = models.FloatField(default=0)
    exit_quote_amount = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = OrderManager()

    def __str__(self):
        return f"ORDER: {self.pk=}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Order ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.connection=}\n"
        string += f"{beacon}\t{self.pair=}\n"
        string += f"{beacon}\t{self.asked_for_amount=}\n"
        string += f"{beacon}\t{self.asked_for_ticker=}\n"
        string += f"{beacon}\t{self.debited_amount=}\n"
        string += f"{beacon}\t{self.batch_share=}\n"
        string += f"{beacon}\t{self.exit_base_amount=}\n"
        string += f"{beacon}\t{self.exit_quote_amount=}\n"
        string += f"{beacon}\t{self.side=}\n"
        string += f"{beacon}\t{self.price=}\n"
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

    def calculate_exit_amounts(self, controller, executed_amounts: dict, save: bool) -> None:
        if self.batch_share != 0:
            if self.side == SIDES.BUY:
                if executed_amounts == {}:
                    self.exit_amount_base = 0
                    self.exit_amount_quote = self.debited_amount
                else:
                    self.exit_amount_base = executed_amounts[controller.base] * self.batch_share
                    self.exit_amount_quote = self.debited_amount + executed_amounts[controller.quote] * self.batch_share
            elif self.side == SIDES.SELL:
                if executed_amounts == {}:
                    self.exit_amount_base = self.debited_amount
                    self.exit_amount_quote = 0
                else:
                    self.exit_amount_base = self.debited_amount + executed_amounts[controller.base] * self.batch_share
                    self.exit_amount_quote = executed_amounts[controller.quote] * self.batch_share
            else:
                error_msg = f"Souldn't be calculating exit amount for order {self.pk} with side {self.side}."
                raise OrderError.ProcessError(error_msg)
        else:
            self.exit_amount_base = 0
            self.exit_amount_quote = 0
        if save:
            self.save()

    def calculate_batch_share(self, total: float, save: bool):
        self.batch_share = self.asked_for_amount / total
        if save:
            self.save()
