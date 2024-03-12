import uuid
from datetime import datetime, timedelta

import pandas as pd
from django.db import models
from django.utils.timezone import get_default_timezone

from django_napse.core.models.histories.managers.history_data_point import HistoryDataPointManager
from django_napse.core.models.histories.managers.history_data_point_field import HistoryDataPointFieldManager
from django_napse.utils.constants import HISTORY_DATAPOINT_FIELDS, HISTORY_DATAPOINT_FIELDS_WILDCARDS
from django_napse.utils.errors import HistoryError
from django_napse.utils.findable_class import FindableClass
from django_napse.utils.usefull_functions import process_value_from_type


class History(FindableClass, models.Model):
    """A History is a collection of data points.

    Use it to track the evolution of a value over time.

    Create a child class to get started.

    The child class should have a ForeignKey to the model you want to track (called `owner`).
    """

    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    def __str__(self) -> str:
        return f"HISTORY {self.uuid}"

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}History {self.pk}:\n"
        string += f"{beacon}\t{self.uuid=}\n"
        string += f"{beacon}\tDataPoints:\n"
        df_string = str(self.to_dataframe()).replace("\n", f"\n{beacon}\t\t")
        string += f"{beacon}\t\t{df_string}\n"
        if verbose:
            print(string)
        return string

    def to_dataframe(self) -> pd.DataFrame:
        """Return a DataFrame containing the data points."""
        all_data_points = self.data_points.all()
        return pd.DataFrame([data_point.to_dict() for data_point in all_data_points])

    @property
    def owner(self) -> models.Model:
        """Return the owner of the history."""
        return self.find().owner

    @classmethod
    def get_or_create(cls, owner: models.Model) -> "History":
        """Return the history of the owner if it exists, else create it."""
        if hasattr(owner, "history"):
            return owner.history
        return cls.objects.create(owner=owner)

    def delta(self, days: int = 30) -> float:
        """Return the value delta between today and {days} days ago."""
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

    def generate_data_point(self) -> "HistoryDataPoint":
        """Create a new data point.

        This method should be implemented in the child class.
        """
        error_msg = "You must implement the generate_data_point method in your child class."
        raise NotImplementedError(error_msg)


class HistoryDataPoint(models.Model):
    """A HistoryDataPoint is a collection of fields."""

    history: "History" = models.ForeignKey(History, on_delete=models.CASCADE, related_name="data_points")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = HistoryDataPointManager()

    def __str__(self) -> str:  # pragma: no cover
        return f"HISTORY DATA POINT {self.pk} {self.history.uuid}"

    def to_dict(self) -> dict:
        """Return a dictionary containing the fields."""
        return {field.key: field.get_value() for field in self.fields.all()}

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}HistoryDataPoint {self.pk}:\n"
        string += f"{beacon}Fields:\n"
        for field in self.fields.all():
            string += field.info(beacon=beacon + "\t", verbose=False)
        if verbose:
            print(string)
        return string


class HistoryDataPointField(models.Model):
    """A HistoryDataPointField is a key-value pair with a target type."""

    history_data_point: "HistoryDataPoint" = models.ForeignKey(HistoryDataPoint, on_delete=models.CASCADE, related_name="fields")
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    target_type = models.CharField(max_length=255)

    objects = HistoryDataPointFieldManager()

    def __str__(self) -> str:  # pragma: no cover
        return f"HISTORY DATA POINT FIELD {self.pk} {self.history_data_point.pk}"

    def save(self, *args, **kwargs):  # noqa
        is_wildcard = False
        for wildcard in HISTORY_DATAPOINT_FIELDS_WILDCARDS:
            if self.key.startswith(wildcard):
                is_wildcard = True
                break
        if self.key not in HISTORY_DATAPOINT_FIELDS and not is_wildcard:
            error_msg = f"Invalid key {self.key} for HistoryDataPointField"
            raise HistoryError.InvalidDataPointFieldKey(error_msg)
        return super().save(*args, **kwargs)

    def info(self, beacon: str = "", *, verbose: bool = True) -> str:
        """Return a string with the model information.

        Args:
            beacon (str, optional): The prefix for each line. Defaults to "".
            verbose (bool, optional): Whether to print the string. Defaults to True.

        Returns:
            str: The string with the history information.
        """
        string = ""
        string += f"{beacon}HistoryDataPointField {self.pk}:\n"
        string += f"{beacon}\t{self.key=}\n"
        string += f"{beacon}\t{self.value=}\n"
        string += f"{beacon}\t{self.target_type=}\n"
        if verbose:
            print(string)
        return string

    def get_value(self) -> any:
        """Return the value as the target type."""
        return process_value_from_type(value=self.value, target_type=self.target_type)
