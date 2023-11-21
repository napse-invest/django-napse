import uuid
from datetime import datetime, timedelta

import pandas as pd
from django.db import models
from django.utils.timezone import get_default_timezone

from django_napse.utils.constants import HISTORY_DATAPOINT_FIELDS
from django_napse.utils.errors import HistoryError
from django_napse.utils.findable_class import FindableClass
from django_napse.utils.usefull_functions import process_value_from_type


class History(FindableClass, models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    def __str__(self) -> str:
        return f"HISTORY {self.uuid}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}History {self.pk}:\n"
        string += f"{beacon}\t{self.uuid=}\n"
        string += f"{beacon}\tDataPoints:\n"
        df_string = str(self.to_dataframe()).replace("\n", f"\n{beacon}\t\t")
        string += f"{beacon}\t\t{df_string}\n"
        if verbose:
            print(string)
        return string

    def to_dataframe(self):
        all_data_points = self.data_points.all()
        return pd.DataFrame([data_point.to_dict() for data_point in all_data_points])

    @property
    def owner(self):
        return self.find().owner

    @classmethod
    def get_or_create(cls, owner):
        if hasattr(owner, "history"):
            return owner.history
        return cls.objects.create(owner=owner)

    def delta(self, days: int = 30) -> float:
        """Return the value delta between today and {days} days ago."""
        # TODO: TEST IT
        date = datetime.now(tz=get_default_timezone()) - timedelta(days=days)
        data_points = self.data_points.filter(created_at__date=date.date())

        while not data_points.exists():
            days -= 1
            date = date + timedelta(days=days)
            data_points = self.data_points.filter(created_at__date=date.date())
            if days == 0 and not data_points.exists():
                return 0
            if data_points.exists():
                break

        return data_points


class HistoryDataPoint(models.Model):
    history = models.ForeignKey(History, on_delete=models.CASCADE, related_name="data_points")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"HISTORY DATA POINT {self.pk} {self.history.uuid}"

    def to_dict(self):
        return {field.key: field.get_value() for field in self.fields.all()}


class HistoryDataPointField(models.Model):
    history_data_point = models.ForeignKey(HistoryDataPoint, on_delete=models.CASCADE, related_name="fields")
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    target_type = models.CharField(max_length=255)

    def __str__(self) -> str:  # pragma: no cover
        return f"HISTORY DATA POINT FIELD {self.pk} {self.history_data_point.pk}"

    def save(self, *args, **kwargs):
        if self.key not in HISTORY_DATAPOINT_FIELDS:
            error_msg = f"Invalid key {self.key} for HistoryDataPointField"
            raise HistoryError.InvalidDataPointFieldKey(error_msg)
        return super().save(*args, **kwargs)

    def get_value(self):
        return process_value_from_type(value=self.value, target_type=self.target_type)
