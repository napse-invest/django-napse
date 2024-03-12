from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from django_napse.core.models.histories.history import HistoryDataPoint, HistoryDataPointField


class HistoryDataPointFieldManager(models.Manager):
    """The manager for the HistoryDataPointField model."""

    def create(
        self,
        history_data_point: "HistoryDataPoint",
        key: str,
        value: str,
    ) -> "HistoryDataPointField":
        """Create a new data point field for a data point."""
        data_point_field = self.model(history_data_point=history_data_point, key=key, value=str(value), target_type=type(value).__name__)
        data_point_field.save()
        return data_point_field
