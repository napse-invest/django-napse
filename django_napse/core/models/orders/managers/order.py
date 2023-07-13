from django.apps import apps
from django.db import models


class OrderManager(models.Manager):
    def create(
        self,
        bot,
        buy_amount: float,
        sell_amount: float,
        price: float,
    ):
        order = self.model(
            bot=bot,
            buy_amount=buy_amount,
            sell_amount=sell_amount,
            price=price,
        )
        order.save()
        OrderWallet = apps.get_model("django_napse_core", "OrderWallet")
        OrderWallet.objects.create(title=f"Wallet for order {order.pk}", owner=order)
        return order
