from __future__ import annotations

from rest_framework import serializers

from django_napse.core.models.histories.history import HistoryDataPointField


class HistoryDataPointFieldSerializer(serializers.ModelSerializer):
    """Serialize a wallet instance."""

    class Meta:  # noqa: D106
        model = HistoryDataPointField
        fields: str = ["key", "value", "target_type"]
