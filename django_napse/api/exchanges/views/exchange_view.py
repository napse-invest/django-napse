from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django_napse.api.exchanges.serializers import ExchangeAccountSerializer
from django_napse.core.models import ExchangeAccount

# from rest_framework.decorators import action


class ExchangeAccountView(GenericViewSet):
    permission_classes = []
    serializer_class = ExchangeAccountSerializer

    def get_queryset(self):
        return ExchangeAccount.objects.all()

    def list(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
