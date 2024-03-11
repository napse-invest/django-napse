from __future__ import annotations

from typing import ClassVar

from rest_framework import serializers

from django_napse.api.histories.serializers.datapoint_field import HistoryDataPointFieldSerializer
from django_napse.core.models.histories.history import HistoryDataPoint


class HistoryDataPointSerializer(serializers.ModelSerializer):
    """Serialize a wallet instance."""

    fields = HistoryDataPointFieldSerializer(many=True)

    class Meta:  # noqa: D106
        model = HistoryDataPoint
        fields: ClassVar[list[str]] = ["created_at", "fields"]
