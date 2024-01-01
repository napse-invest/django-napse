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

    def get_serializer_class(self, *args, **kwargs):
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

    def get_object(self):
        uuid = self.kwargs.get("pk", None)
        if uuid is None:
            return super().get_object()
        return Fleet.objects.get(uuid=uuid)

    def list(self, request):
        space_containers = request.query_params.get("space_containers", True)
        space_uuid = request.query_params.get("space", None)
        api_key = self.get_api_key(request)

        if not space_containers and api_key.is_master_key:
            # Not space_containers mode is only available for master key
            serializer = self.get_serializer(self.get_queryset(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Get spaces from API key
        spaces = NapseSpace.objects.all() if api_key.is_master_key else [permission.space for permission in api_key.permissions.all()]

        # Filter by specific space
        if space_uuid is not None:
            space = NapseSpace.objects.get(uuid=space_uuid)
            if space not in spaces:
                return Response(status=status.HTTP_403_FORBIDDEN)
            spaces = [space]

        # Fleet list
        fleets = []
        for space in spaces:
            print("FLEET", space.fleets)
            serializer = self.get_serializer(space.fleets, many=True)
            if serializer.data != []:
                fleets += serializer.data
        return Response(fleets, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        space = self.get_space(request)
        serializer = self.get_serializer(instance, space=space)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        space = self.get_space(request)
        serializer = self.get_serializer(data=request.data, space=space)
        serializer.is_valid(raise_exception=True)
        fleet = serializer.save()
        fleet.invest(space, 0, "USDT")
        return Response(status=status.HTTP_201_CREATED)

    def delete(self):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
