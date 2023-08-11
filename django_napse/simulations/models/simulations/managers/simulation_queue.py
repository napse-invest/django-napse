from datetime import datetime

from django.apps import apps
from django.db import models


class SimulationQueueManager(models.Manager):
    def create(
        self,
        space,
        bot,
        start_date: datetime,
        end_date: datetime,
        investments: dict,
    ):
        SimulationQueueInvestedCurrency = apps.get_model("django_napse_simulations", "SimulationQueueInvestedCurrency")
        queue = self.model(
            space=space,
            bot=bot,
            start_date=start_date,
            end_date=end_date,
        )
        queue.save()
        for ticker, investment in investments.items():
            SimulationQueueInvestedCurrency.objects.create(
                owner=queue,
                ticker=ticker,
                amount=investment,
            )
        return queue
