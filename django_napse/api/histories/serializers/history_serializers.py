from rest_framework import serializers

from django_napse.core.models.histories.history import History, HistoryDataPoint, HistoryDataPointField


class HistorySerializer(serializers.Serializer):
    data_points = HistoryDataPoint(many=True, read_only=True)

    class Meta:
        model = History
        fields = ["data_points"]


class HistoryDataPointSerializer(serializers.Serializer):
    fields = HistoryDataPointField(many=True, read_only=True)

    class Meta:
        model = HistoryDataPoint
        fields = [
            "fields",
        ]


class HistoryDataPointFieldSerializer(serializers.Serializer):
    class Meta:
        model = HistoryDataPointField
        fields = [
            "key",
            "value",
            "target_type",
        ]
        read_only_fields = fields
