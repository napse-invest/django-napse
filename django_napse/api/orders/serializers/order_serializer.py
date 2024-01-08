from rest_framework import serializers

from django_napse.core.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
