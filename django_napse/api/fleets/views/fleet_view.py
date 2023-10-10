from rest_framework import status
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from django_napse.api.custom_permissions import HasSpace
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.fleets.serializers import FleetDetailSerializer, FleetSerializer
from django_napse.core.models import NapseSpace


class FleetView(CustomViewSet):
    permission_classes = [HasAPIKey, HasSpace]
    serializer_class = FleetSerializer

    def get_queryset(self):
        self.space = NapseSpace.objects.get(uuid=self.request.query_params["space"])
        return self.space.fleets

    def get_serialiser_class(self, *args, **kwargs):
        actions: dict = {
            "list": FleetSerializer,
            "retrieve": FleetDetailSerializer,
            "create": FleetSerializer,
        }
        result = actions.get(self.action)
        return result if result else super().get_serializer_class()

    def list(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True, space=self.space)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        pass

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
