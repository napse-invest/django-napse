from django.db.models import QuerySet
from rest_framework import status
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from django_napse.api.bots.serializers.bot_serializers import BotDetailSerializer, BotSerializer
from django_napse.api.custom_permissions import HasSpace
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.core.models import Bot, Space
from django_napse.utils.errors import APIError


class BotView(CustomViewSet):
    permission_classes = [HasAPIKey, HasSpace]
    serializer_class = BotSerializer

    def get_queryset(self) -> list[QuerySet[Bot]] | dict[str, QuerySet[Bot]]:
        """Return bot queryset.

        Can return
            Free bots across all available spaces
            Bots with connections without space containerization
            Bots with connections with a specific space containerization
            Bots with connections with space containerization

        Raises:
            ValueError: Not space_containers mode is only available for master key.
            ValueError: Space not found.
        """
        api_key = self.get_api_key(self.request)
        spaces = Space.objects.all() if api_key.is_master_key else [permission.space for permission in api_key.permissions.all()]

        # Free bots across all available spaces
        if self.request.query_params.get("free", False):
            # Exchange account containerization
            request_space = self.get_space(self.request)
            if request_space is None:
                raise APIError.MissingSpace()
            spaces = [space for space in spaces if space.exchange_account == request_space.exchange_account]
            # Cross space free bots
            return [bot for bot in Bot.objects.filter(strategy__config__space__in=spaces) if bot.is_free]

        # Bots with connections without space containerization
        if not self.request.query_params.get("space_containers", True):
            if not api_key.is_master_key:
                error_msg: str = "Not space_containers mode is only available for master key."
                raise ValueError(error_msg)
            return Bot.objects.exclude(connections__isnull=True)

        # Filter by specific space
        space_uuid = self.request.query_params.get("space", None)
        if space_uuid is not None:
            for space in spaces:
                if space.uuid == space_uuid:
                    spaces = [space]
                    break
            else:
                error_msg: str = "Space not found."
                raise ValueError(error_msg)

        # Space container mode
        bots_per_space: dict[str, QuerySet[Bot]] = {}
        for space in spaces:
            bots_per_space[space] = space.bots.exclude(connections__isnull=True)
        return bots_per_space

    def get_serializer_class(self, *args, **kwargs):
        actions: dict = {
            "list": BotSerializer,
            "retrieve": BotDetailSerializer,
        }
        result = actions.get(self.action)
        return result if result else super().get_serializer_class()

    def get_permissions(self):
        match self.action:
            case "list" | "create":
                return [HasAPIKey()]
            case _:
                return super().get_permissions()

    def get_object(self):
        uuid = self.kwargs.get("pk", None)
        if uuid is None:
            return super().get_object()
        return Bot.objects.get(uuid=uuid)

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
        """Return a list of bots.

        Warning: space_containers can lead to undesirable behaviour.
        """
        try:
            queryset = self.get_queryset()
        except ValueError as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(queryset, list):
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if isinstance(queryset, dict):
            serialized_bots: QuerySet[Bot] = []
            for space, query in queryset.items():
                serializer = self.get_serializer(query, many=True, space=space)
                if serializer.data != []:
                    serialized_bots += serializer.data
            return Response(serialized_bots, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        space = self.get_space(request)
        serializer = self.get_serializer(instance, space=space)
        return Response(serializer.data, status=status.HTTP_200_OK)
