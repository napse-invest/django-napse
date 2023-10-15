from rest_framework import status
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from django_napse.api.bots.serializers.bot_serializers import BotSerializer
from django_napse.api.custom_permissions import HasSpace
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.core.models import Bot


class BotView(CustomViewSet):
    permission_classes = [HasAPIKey, HasSpace]
    serializer_class = BotSerializer

    def get_queryset(self):
        return Bot.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        actions: dict = {
            "list": BotSerializer,
        }
        result = actions.get(self.action)
        return result if result else super().get_serializer_class()

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
