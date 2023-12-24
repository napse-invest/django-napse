from rest_framework import status
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from django_napse.api.custom_permissions import HasSpace
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.fleets.serializers import FleetDetailSerializer, FleetSerializer
from django_napse.core.models import Fleet, NapseSpace


class FleetView(CustomViewSet):
    """View of a fleet.

    Query parameters:
        space: uuid of the space to filter on.
        space_containers (bool): If True, list endpoint returns fleets for each space (default = True).
    """

    permission_classes = [HasAPIKey, HasSpace]
    serializer_class = FleetSerializer

    def get_queryset(self):
        space_uuid = self.request.query_params.get("space", None)
        if space_uuid is None:
            return Fleet.objects.all()
        self.get_space = NapseSpace.objects.get(uuid=space_uuid)
        return self.get_space.fleets

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
            case "list":
                return [HasAPIKey()]
            case _:
                return super().get_permissions()

    def list(self, request):
        space_containers = request.query_params.get("space_containers", True)
        if not space_containers:
            serializer = self.serializer_class(self.get_queryset(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Get spaces from API key
        api_key = self.get_api_key(request)
        spaces = NapseSpace.objects.all() if api_key.is_master_key else [permission.space for permission in api_key.permissions.all()]
        fleets = []
        for space in spaces:
            print("FLEET", space.fleets)
            serializer = self.serializer_class(space.fleets, many=True)
            if serializer.data != []:
                fleets.append(*serializer.data)
        return Response(fleets, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        pass

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
        space = self.get_space(request)
        serializer = self.serializer_class(data=request.data, space=space)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def delete(self):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
