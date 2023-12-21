from rest_framework import status
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from django_napse.api.custom_permissions import HasSpace
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.fleets.serializers import FleetDetailSerializer, FleetSerializer
from django_napse.core.models import Fleet, NapseSpace


class FleetView(CustomViewSet):
    permission_classes = [HasAPIKey, HasSpace]
    serializer_class = FleetSerializer

    def get_queryset(self):
        space_uuid = self.request.query_params.get("space", None)
        if space_uuid is None:
            return Fleet.objects.all()
        self.space = NapseSpace.objects.get(uuid=space_uuid)
        return self.space.fleets

    def get_serialiser_class(self, *args, **kwargs):
        actions: dict = {
            "list": FleetSerializer,
            "retrieve": FleetDetailSerializer,
            "create": FleetSerializer,
        }
        result = actions.get(self.action)
        return result if result else super().get_serializer_class()

    def get_permissions(self):
        match self.action:
            case "list" | "create":
                return [HasAPIKey()]
            case _:
                return super().get_permissions()

    def list(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True, space=self.space)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        pass

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
        # serializer = self.serializer_class(data=request.data, space=self.space)

    def delete(self):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
