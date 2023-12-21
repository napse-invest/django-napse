from rest_framework import serializers

from django_napse.api.bots.serializers import BotSerializer
from django_napse.core.models import Cluster


class ClusterSerializer(serializers.ModelSerializer):
    template_bot = BotSerializer()

    class Meta:
        model = Cluster
        fields = [
            "template_bot",
            "share",
            "breakpoint",
            "autoscale",
        ]
