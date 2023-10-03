from django_napse.core.models import Fleet
from rest_framework import serializers
from rest_framework.fields import empty


class FleetSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, space=None, **kwargs):
        self.space = space
        super().__init__(instance=instance, data=data, **kwargs)

    space_frame_value = serializers.SerializerMethodField(read_only=True)
    bot_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Fleet
        fields = [
            "id",
            "name",
            "space_frame_value",
            "bot_count",
        ]
        read_only_fields = [
            "id",
            "space_frame_value",
            "bot_count",
        ]

    def get_space_frame_value(self, instance):
        return instance.space_frame_value(space=self.space)

    def get_bot_count(self, instance):
        return instance.bots.count()
