from typing import TYPE_CHECKING, Optional

from django.apps import apps
from django.db import models

if TYPE_CHECKING:
    from django_napse.core.models.histories.history import History, HistoryDataPoint


class HistoryDataPointManager(models.Manager):
    """The manager for the HistoryDataPoint model."""

    def create(
        self,
        history: "History",
        points: Optional[dict] = None,
    ) -> "HistoryDataPoint":
        """Create a new data point for the history."""
        HistoryDataPointField = apps.get_model("django_napse_core", "HistoryDataPointField")
        points = points or {}
        data_point = self.model(history=history)
        data_point.save()
        for key, value in points.items():
            HistoryDataPointField.objects.create(history_data_point=data_point, key=key, value=value)
        return data_point
