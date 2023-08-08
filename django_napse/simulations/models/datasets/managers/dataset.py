from datetime import datetime

from django.db import models


class DataSetManager(models.Manager):
    def create(self, controller, start_date: datetime, end_date: datetime):
        try:
            dataset = self.model.objects.get(controller=controller)
        except self.model.DoesNotExist:
            dataset = self.model(
                controller=controller,
            )
            dataset.save()
        return dataset.controller.download(
            start_date=start_date,
            end_date=end_date,
        )
