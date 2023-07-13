from django.db import models


class DataSet(models.Model):
    pair = models.CharField(max_length=10)
    interval = models.CharField(max_length=3)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    last_update = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, default="IDLE")
    completion = models.FloatField(default=0.0)
    eta = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ("pair", "interval")

    def __str__(self):  # pragma: no cover
        return f"DATASET: {self.pk=}, {self.pair=}, {self.interval=}, {self.start_date=}, {self.end_date=}"


class Candle(models.Model):
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name="candles")
    open_time = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()

    class Meta:
        unique_together = ("dataset", "open_time")

    def __str__(self):  # pragma: no cover
        return f"{self.open_time} - {self.open} - {self.high} - {self.low} - {self.close} - {self.volume}"


class DataSetQueue(models.Model):
    interval = models.CharField(max_length=3)
    pair = models.CharField(max_length=10)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"DATASET_QUEUE: {self.pk=}, interval={self.interval}, pair={self.pair}, start_date={self.start_date}, end_date={self.end_date}"
