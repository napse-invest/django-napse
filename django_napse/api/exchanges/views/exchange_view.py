from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django_napse.api.exchanges.serializers import ExchangeAccountDetailSerializer, ExchangeAccountSerializer
from django_napse.core.models import ExchangeAccount

# from rest_framework.decorators import action


class ExchangeAccountView(GenericViewSet):
    permission_classes = []

    def get_queryset(self):
        return ExchangeAccount.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        actions: dict = {
            "list": ExchangeAccountSerializer,
            "retrieve": ExchangeAccountDetailSerializer,
        }
        result = actions.get(self.action)
        return result if result else super().get_serializer_class()

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
