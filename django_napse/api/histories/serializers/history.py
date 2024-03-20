from __future__ import annotations

from typing import ClassVar

from rest_framework import serializers

from django_napse.api.histories.serializers.datapoint import HistoryDataPointSerializer
from django_napse.core.models.histories.history import History


class HistorySerializer(serializers.ModelSerializer):
    """Serialize a wallet instance."""

    data_points = HistoryDataPointSerializer(many=True)

    class Meta:  # noqa: D106
        model = History
        fields: ClassVar[list[str]] = [
            "uuid",
            "data_points",
        ]
