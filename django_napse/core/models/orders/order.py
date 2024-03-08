from typing import TYPE_CHECKING, Optional

from django.db import models

from django_napse.core.models.orders.managers import OrderManager
from django_napse.core.models.transactions.credit import Credit
from django_napse.core.models.transactions.debit import Debit
from django_napse.core.models.transactions.transaction import Transaction
from django_napse.utils.constants import EXCHANGE_PAIRS, MODIFICATION_STATUS, ORDER_STATUS, SIDES, TRANSACTION_TYPES
from django_napse.utils.errors import OrderError

if TYPE_CHECKING:
    from django_napse.core.models.accounts.exchange import ExchangeAccount
    from django_napse.core.models.bots.controller import Controller
    from django_napse.core.models.modifications.modification import Modification


class OrderBatch(models.Model):
    """Represent a batch of bots' orders."""

    status = models.CharField(default=ORDER_STATUS.PENDING, max_length=15)
    controller: "Controller" = models.ForeignKey("Controller", on_delete=models.CASCADE, related_name="order_batches")

    def __str__(self) -> str:
        return f"ORDER BATCH {self.pk}"

    def set_status_ready(self) -> None:
        """Change status of the batch from PENDING to READY."""
        if self.status == ORDER_STATUS.PENDING:
            self.status = ORDER_STATUS.READY
            self.save()
        else:
            error_msg = f"Order {self.pk} is not pending."
            raise OrderError.StatusError(error_msg)

    def _set_status_post_process(self, receipt: dict) -> None:
        if self.status != ORDER_STATUS.READY:
            error_msg = f"Order {self.pk} is not ready."
            raise OrderError.StatusError(error_msg)
        buy_failed = False
        sell_failed = False
        if "error" in receipt[SIDES.BUY]:
            buy_failed = True
        if "error" in receipt[SIDES.SELL]:
            sell_failed = True
        if buy_failed and sell_failed:
            self.status = ORDER_STATUS.FAILED
        elif buy_failed:
            self.status = ORDER_STATUS.ONLY_SELL_PASSED
        elif sell_failed:
            self.status = ORDER_STATUS.ONLY_BUY_PASSED
        else:
            self.status = ORDER_STATUS.PASSED


class Order(models.Model):
    """An order market created by bots."""

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
    exit_amount_base = models.FloatField(default=0)
    exit_amount_quote = models.FloatField(default=0)
    fees = models.FloatField(default=0)
    fee_ticker = models.CharField(max_length=10, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = OrderManager()

    def __str__(self) -> str:
        return f"ORDER: {self.pk=}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}Order ({self.pk=}):\n"
        string += f"{beacon}Args:\n"
        string += f"{beacon}\t{self.connection=}\n"
        string += f"{beacon}\t{self.pair=}\n"
        string += f"{beacon}\t{self.asked_for_amount=}\n"
        string += f"{beacon}\t{self.asked_for_ticker=}\n"
        string += f"{beacon}\t{self.debited_amount=}\n"
        string += f"{beacon}\t{self.batch_share=}\n"
        string += f"{beacon}\t{self.exit_amount_base=}\n"
        string += f"{beacon}\t{self.exit_amount_quote=}\n"
        string += f"{beacon}\t{self.fees=}\n"
        string += f"{beacon}\t{self.fee_ticker=}\n"
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
    def testing(self) -> bool:
        """Whether the order is in testing mode.

        Returns:
            bool: Whether the order is in testing mode.
        """
        return self.connection.testing

    @property
    def exchange_account(self) -> "ExchangeAccount":
        """Return the exchange account of the order.

        Returns:
            ExchangeAccount: The exchange account of the order.
        """
        return self.connection.wallet.exchange_account

    def calculate_exit_amounts(self, controller: "Controller", executed_amounts: dict, fees: dict) -> None:
        """Calculate the exit amounts of the order.

        Exit amounts are the amounts that will be received by the user after the order is completed.

        Args:
            controller (Controller): The controller associated with the order.
            executed_amounts (dict): The amounts executed by the order.
            fees (dict): The fees paid by the user.

        Raises:
            OrderError.ProcessError: If the side of the order is not SELL or BUY.
        """
        if self.batch_share != 0:
            if self.side == SIDES.BUY:
                if executed_amounts == {}:
                    self.exit_amount_base = 0
                    self.exit_amount_quote = self.debited_amount
                    self.fees = 0
                    self.fee_ticker = controller.base
                else:
                    self.exit_amount_base = executed_amounts[controller.base] * self.batch_share
                    self.exit_amount_quote = self.debited_amount + executed_amounts[controller.quote] * self.batch_share
                    self.fees = fees[controller.base] * self.batch_share
                    self.fee_ticker = controller.base
            elif self.side == SIDES.SELL:
                if executed_amounts == {}:
                    self.exit_amount_base = self.debited_amount
                    self.exit_amount_quote = 0
                    self.fees = 0
                    self.fee_ticker = controller.quote
                else:
                    self.exit_amount_base = self.debited_amount + executed_amounts[controller.base] * self.batch_share
                    self.exit_amount_quote = executed_amounts[controller.quote] * self.batch_share
                    self.fees = fees[controller.quote] * self.batch_share
                    self.fee_ticker = controller.quote
            else:
                error_msg = f"Souldn't be calculating exit amount for order {self.pk} with side {self.side}."
                raise OrderError.ProcessError(error_msg)
        else:
            self.exit_amount_base = 0
            self.exit_amount_quote = 0
            self.fees = 0
            self.fee_ticker = controller.base

    def calculate_batch_share(self, total: float) -> None:
        """Set the batch share of the order.

        The batch share is the share of the total amount of the batch that the order represents.
        """
        self.batch_share = self.asked_for_amount / total

    def passed(self, batch: Optional[OrderBatch] = None) -> bool:
        """Whether the order passed or not.

        Args:
            batch (Optional[OrderBatch], optional): The batch to check. Defaults to None.

        Returns:
            bool: Whether the order passed or not.
        """
        batch = batch or self.batch
        return (self.side == SIDES.BUY and (batch.status in (ORDER_STATUS.PASSED, ORDER_STATUS.ONLY_BUY_PASSED))) or (
            self.side == SIDES.SELL and (batch.status in (ORDER_STATUS.PASSED, ORDER_STATUS.ONLY_SELL_PASSED))
        )

    def apply_modifications__no_db(
        self,
        batch: OrderBatch,
        modifications: list["Modification"],
        **kwargs: dict,
    ) -> tuple[list[models.Model], list["Modification"]]:
        """Apply the modifications to the order.

        Returns:
            all_modifications (list[Modification]): The modifications applied to the order.

        """
        all_modifications = []
        all_modified_objects = []
        if self.passed(batch):
            for modification in modifications:
                modified_object, modification_object = modification.apply__no_db(order=self, **kwargs)
                all_modifications.append(modification_object)
                all_modified_objects.append(modified_object)
        else:
            for modification in [modification for modification in modifications if modification.ignore_failed_order]:
                modified_object, modification_object = modification.apply__no_db(order=self, **kwargs)
                all_modifications.append(modification_object)
                all_modified_objects.append(modified_object)
            for modification in [modification for modification in modifications if not modification.ignore_failed_order]:
                modification.status = MODIFICATION_STATUS.REJECTED
                all_modifications.append(modification)
        return all_modifications, all_modified_objects

    def apply_modifications(self) -> list["Modification"]:
        """Apply the modifications to the order, and save them to the database.

        Returns:
            list[Modification]: The modifications applied to the order.
        """
        modifications, modified_objects = self.apply_modifications__no_db(
            batch=self.batch,
            modifications=[modification.find() for modification in self.modifications.all()],
            strategy=self.connection.bot.strategy.find(),
            architecture=self.connection.bot.architecture.find(),
            currencies=self.connection.wallet.to_dict().currencies,
        )
        for modification in modifications:
            modification.save()
        for modified_object in modified_objects:
            modified_object.save()
        return modifications

    def apply_swap(self) -> None:
        """Swap quote into base (BUY) or base into quote (SELL)."""
        if self.side == SIDES.BUY:
            Debit.objects.create(
                wallet=self.wallet,
                amount=self.debited_amount - self.exit_amount_quote,
                ticker=self.batch.controller.quote,
            )
            Credit.objects.create(
                wallet=self.wallet,
                amount=self.exit_amount_base,
                ticker=self.batch.controller.base,
            )
        elif self.side == SIDES.SELL:
            Debit.objects.create(
                wallet=self.wallet,
                amount=self.debited_amount - self.exit_amount_base,
                ticker=self.batch.controller.base,
            )
            Credit.objects.create(
                wallet=self.wallet,
                amount=self.exit_amount_quote,
                ticker=self.batch.controller.quote,
            )

    def process_payout(self) -> None:
        """Make a payout or a refund depending on the passed() status."""
        if self.side == SIDES.KEEP:
            return
        if self.passed():
            Transaction.objects.create(
                from_wallet=self.wallet,
                to_wallet=self.connection.wallet,
                amount=self.exit_amount_base,
                ticker=self.batch.controller.base,
                transaction_type=TRANSACTION_TYPES.ORDER_PAYOUT,
            )
            Transaction.objects.create(
                from_wallet=self.wallet,
                to_wallet=self.connection.wallet,
                amount=self.exit_amount_quote,
                ticker=self.batch.controller.quote,
                transaction_type=TRANSACTION_TYPES.ORDER_PAYOUT,
            )
        else:
            Transaction.objects.create(
                from_wallet=self.wallet,
                to_wallet=self.connection.wallet,
                amount=self.exit_amount_base,
                ticker=self.batch.controller.base,
                transaction_type=TRANSACTION_TYPES.ORDER_REFUND,
            )
            Transaction.objects.create(
                from_wallet=self.wallet,
                to_wallet=self.connection.wallet,
                amount=self.exit_amount_quote,
                ticker=self.batch.controller.quote,
                transaction_type=TRANSACTION_TYPES.ORDER_REFUND,
            )

    def tickers_info(self) -> dict[str, str]:
        """Give informations about received, spent & fee tickers."""
        spent_ticker = EXCHANGE_PAIRS[self.connection.space.exchange_account.exchange.name][self.pair]["base" if self.side == SIDES.SELL else "quote"]
        received_ticker = EXCHANGE_PAIRS[self.connection.space.exchange_account.exchange.name][self.pair][
            "quote" if self.side == SIDES.SELL else "base"
        ]
        fee_ticker = self.fee_ticker

        return {
            "spent_ticker": spent_ticker,
            "received_ticker": received_ticker,
            "fee_ticker": fee_ticker,
        }
