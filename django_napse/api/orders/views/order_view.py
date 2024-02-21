from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.orders.serializers import OrderSerializer
from django_napse.core.models import Order


class OrderView(CustomViewSet):
    """."""

    # permission_classes = [HasAPIKey, HasSpace]
    permission_classes = []
    serializer_class = OrderSerializer

    def get_queryset(self):
        print(f"count: {Order.objects.count()}")
        return Order.objects.all()

    def list(self, request):
        """For test & debug purposes only."""
        if not settings.DEBUG:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
