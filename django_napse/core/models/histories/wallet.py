from typing import TYPE_CHECKING

from django.db import models

from django_napse.core.models.histories.history import History, HistoryDataPoint
from django_napse.utils.constants import HISTORY_DATAPOINT_FIELDS, HISTORY_DATAPOINT_FIELDS_WILDCARDS

if TYPE_CHECKING:
    from django_napse.core.models.wallets.wallet import Wallet


class WalletHistory(History):
    """A History for a Wallet.

    Use it to track the evolution of a bot over time.

    This tracks the following fields:
    - `value`: The value of the wallet in USD.
    - `amount_ticker`: For each ticker, the amount of the ticker in the wallet.
    """

    owner: "Wallet" = models.OneToOneField("Wallet", on_delete=models.CASCADE, related_name="history")

    def generate_data_point(self) -> "HistoryDataPoint":
        """Create a new data point for the bot."""
        wallet = self.owner.to_dict()
        points = {
            HISTORY_DATAPOINT_FIELDS.WALLET_VALUE: self.owner.value_market(),
        }
        for currency in wallet.currencies.values():
            points[HISTORY_DATAPOINT_FIELDS_WILDCARDS.AMOUNT + currency.ticker] = currency.amount

        return HistoryDataPoint.objects.create(
            history=self,
            points=points,
        )
