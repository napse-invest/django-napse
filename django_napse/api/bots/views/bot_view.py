from rest_framework import status
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from django_napse.api.bots.serializers.bot_serializers import BotSerializer
from django_napse.api.custom_permissions import HasSpace
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.core.models import Bot, NapseSpace


class BotView(CustomViewSet):
    permission_classes = [HasAPIKey, HasSpace]
    serializer_class = BotSerializer

    def get_queryset(self):
        return Bot.objects.exclude(connections__isnull=True)

    def get_serializer_class(self, *args, **kwargs):
        actions: dict = {
            "list": BotSerializer,
        }
        result = actions.get(self.action)
        return result if result else super().get_serializer_class()

    def get_permissions(self):
        match self.action:
            case "list" | "create":
                return [HasAPIKey()]
            case _:
                return super().get_permissions()

    def _get_boolean_query_param(self, param: str) -> bool | None:
        """Return None if a boolean cannot be found."""
        if isinstance(param, bool):
            return param

        if not isinstance(param, str):
            return None

        match param.lower():
            case "true" | "1":
                return True
            case "false" | "0":
                return False
            case _:
                return None

    def list(self, request):
        space_containers = self._get_boolean_query_param(request.query_params.get("space_containers", True))
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

        # Bot list
        bots = []
        for space in spaces:
            serializer = self.get_serializer(space.bots, many=True, space=space)
            if serializer.data != []:
                bots += serializer.data
        return Response(bots, status=status.HTTP_200_OK)

        # TODO: make space containerization
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
