from datetime import timedelta

import pandas as pd
from binance.helpers import interval_to_milliseconds
from django.db import models

from django_napse.simulations.models.datasets.managers.dataset import DataSetManager
from django_napse.utils.constants import DOWNLOAD_STATUS
from django_napse.utils.errors import DataSetError


class DataSet(models.Model):
    controller = models.OneToOneField("django_napse_core.Controller", on_delete=models.CASCADE, related_name="dataset")
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    last_update = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, default=DOWNLOAD_STATUS.IDLE)
    completion = models.FloatField(default=0.0)
    eta = models.DurationField(null=True, blank=True)

    objects = DataSetManager()

    def __str__(self):
        return f"DATASET: {self.pk=}"

    def save(self, *args, **kwargs):
        if self.completion < 0 or self.completion > 100:
            error_msg = f"Completion ({self.completion}) not in [0, 100]"
            raise DataSetError.InvalidSettings(error_msg)

        if self.status not in str(DOWNLOAD_STATUS):
            error_msg = f"Status ({self.status}) not in {DOWNLOAD_STATUS}"
            raise DataSetError.InvalidSettings(error_msg)

        query = Candle.objects.filter(dataset=self).order_by("open_time")
        number_of_candles = query.count()
        if number_of_candles > 0:
            self.start_date = query[0].open_time
            self.end_date = query[number_of_candles - 1].open_time + timedelta(milliseconds=interval_to_milliseconds(self.controller.interval) - 1)
        super().save(*args, **kwargs)

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Dataset {self.pk}:\n"
        string += f"{beacon}\t{self.controller=}\n"
        string += f"{beacon}\t{self.start_date=}\n"
        string += f"{beacon}\t{self.end_date=}\n"
        string += f"{beacon}\t{self.last_update=}\n"
        string += f"{beacon}\t{self.status=}\n"
        string += f"{beacon}\t{self.completion=}\n"
        string += f"{beacon}\t{self.eta=}\n"
        string += f"{beacon}Candles:\n"
        candles = self.candles.all().order_by("open_time")
        if candles.count() > 10:
            for candle in candles[:5]:
                string += f"{beacon}\tO:{candle.open_time}\t H: {candle.high}\t L: {candle.close}\t C: {candle.low}\t V: {candle.volume}\n"
            string += f"{beacon}\t...\n"
            for candle in candles[candles.count() - 5 :]:
                string += f"{beacon}\tO:{candle.open_time}\t H: {candle.high}\t L: {candle.close}\t C: {candle.low}\t V: {candle.volume}\n"
            string += f"{beacon}\t({candles.count()} candles)\n"
        else:
            for candle in candles:
                string += f"{beacon}\tO:{candle.open_time}\t H: {candle.high}\t L: {candle.close}\t C: {candle.low}\t V: {candle.volume}\n"

        if verbose:
            print(string)
        return string

    def create_candles(self, candles: list):
        """Save a list of candle Objects into the database."""
        Candle.objects.bulk_create(candles)

    def set_downloading(self):
        """Set the dataset status to downloading.

        Raises:
            ValueError: If the dataset isn't in IDLE status.
        """
        if self.status == DOWNLOAD_STATUS.IDLE:
            self.status = DOWNLOAD_STATUS.DOWNLOADING
            self.completion = 0
            self.save()
        else:
            error_msg = "Dataset is already downloading."
            raise DataSetError.InvalidSettings(error_msg)

    def set_idle(self):
        """Set the dataset status to idle."""
        if self.status == DOWNLOAD_STATUS.DOWNLOADING:
            self.status = DOWNLOAD_STATUS.IDLE
            self.save()
        else:
            error_msg = "Dataset is not downloading."
            raise DataSetError.InvalidSettings(error_msg)

    def is_finished(self):
        return self.status == DOWNLOAD_STATUS.IDLE and self.completion == 100

    def to_dataframe(self, start_date=None, end_date=None):
        start_date = start_date or self.start_date
        end_date = end_date or self.end_date
        candles = self.candles.filter(open_time__gte=start_date, open_time__lt=end_date).order_by("open_time")
        return pd.DataFrame(
            data={
                "open_time": [candle.open_time for candle in candles],
                "open": [candle.open for candle in candles],
                "high": [candle.high for candle in candles],
                "low": [candle.low for candle in candles],
                "close": [candle.close for candle in candles],
                "volume": [candle.volume for candle in candles],
            },
        )


class Candle(models.Model):
    dataset = models.ForeignKey("DataSet", on_delete=models.CASCADE, related_name="candles")
    open_time = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()

    class Meta:
        unique_together = ("dataset", "open_time")

    def __str__(self):
        return f"CANDLE: {self.pk=}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Candle {self.pk}:\n"
        string += f"{beacon}\t{self.dataset=}\n"
        string += f"{beacon}\t{self.open_time=}\n"
        string += f"{beacon}\t{self.open=}\n"
        string += f"{beacon}\t{self.high=}\n"
        string += f"{beacon}\t{self.low=}\n"
        string += f"{beacon}\t{self.close=}\n"
        string += f"{beacon}\t{self.volume=}\n"

        if verbose:
            print(string)
        return string

    def to_dict(self):
        return {
            "controller": self.dataset.controller,
            "open_time": self.open_time,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "extra": {},
        }


class DataSetQueue(models.Model):
    controller = models.ForeignKey("django_napse_core.Controller", on_delete=models.CASCADE, related_name="dataset_queues")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"DATASET_QUEUE: {self.pk=}"

    def get_dataset(self) -> DataSet:
        try:
            return DataSet.objects.get(controller=self.controller)
        except DataSet.DoesNotExist:
            return None
            return None
