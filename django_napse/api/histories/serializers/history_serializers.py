from rest_framework import serializers

from django_napse.core.models.histories.history import History, HistoryDataPoint, HistoryDataPointField


class HistoryDataPointFieldSerializer(serializers.Serializer):
    class Meta:
        model = HistoryDataPointField
        fields = [
            "key",
            "value",
            "target_type",
        ]
        read_only_fields = fields


class HistoryDataPointSerializer(serializers.Serializer):
    fields = HistoryDataPointFieldSerializer(many=True, read_only=True)

    class Meta:
        model = HistoryDataPoint
        fields = [
            "fields",
        ]


class HistorySerializer(serializers.Serializer):
    data_points = HistoryDataPointSerializer(many=True, read_only=True)

    class Meta:
        model = History
        fields = ["data_points"]
