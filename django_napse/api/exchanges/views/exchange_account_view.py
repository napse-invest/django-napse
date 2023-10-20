from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from django_napse.api.custom_permissions import HasMasterKey
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.exchanges.serializers import ExchangeAccountDetailSerializer, ExchangeAccountSerializer
from django_napse.core.models import Exchange, ExchangeAccount
from django_napse.utils.constants import EXCHANGES


class ExchangeAccountView(CustomViewSet):
    permission_classes = [HasMasterKey]
    serializer_class = ExchangeAccountSerializer

    def get_object(self):
        return self.get_queryset().get(uuid=self.kwargs["pk"])

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

    def create(self, request):
        if "name" not in request.data:
            return Response({"error": "Missing name"}, status=status.HTTP_400_BAD_REQUEST)
        if "exchange" not in request.data:
            return Response({"error": "Missing exchange"}, status=status.HTTP_400_BAD_REQUEST)
        if "testing" not in request.data:
            return Response({"error": "Missing testing"}, status=status.HTTP_400_BAD_REQUEST)
        exchange = Exchange.objects.get(name=request.data["exchange"])
        exchange_account = ExchangeAccount.objects.create(
            exchange=exchange,
            name=request.data["name"],
            testing=request.data["testing"],
        )
        serializer = self.get_serializer(exchange_account)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk=None):
        instance = self.get_object()
        if "name" in request.data:
            instance.name = request.data["name"]
        if "description" in request.data:
            instance.description = request.data["description"]
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def possible_exchanges(self, request):
        return Response(list(EXCHANGES), status=status.HTTP_200_OK)
