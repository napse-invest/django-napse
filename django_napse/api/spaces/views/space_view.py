from rest_framework import status
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from django_napse.api.custom_permissions import HasFullAccessPermission, HasMasterKey, HasReadPermission
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.spaces.serializers import SpaceDetailSerializer, SpaceSerializer
from django_napse.core.models import NapseSpace
from django_napse.utils.errors import SpaceError


class SpaceView(CustomViewSet):
    permission_classes = [HasFullAccessPermission]
    serializer_class = SpaceSerializer

    def get_object(self):
        return self.get_queryset().get(uuid=self.kwargs["pk"])

    def get_queryset(self):
        return NapseSpace.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        actions: dict = {
            "list": SpaceSerializer,
            "retrieve": SpaceDetailSerializer,
            "create": SpaceSerializer,
            "update": SpaceSerializer,
            "partial_update": SpaceSerializer,
        }
        result = actions.get(self.action, None)
        return result if result else super().get_serializer_class()

    def get_permissions(self):
        match self.action:
            case "retrieve":
                return [HasReadPermission()]
            case "list":
                return [HasAPIKey()]
            case "create":
                return [HasMasterKey()]

            case _:
                return super().get_permissions()

    def list(self, request):
        api_key = self.get_api_key(request)
        spaces = NapseSpace.objects.all() if api_key.is_master_key else NapseSpace.objects.filter(permissions__in=api_key.permissions.all())
        serializer = self.get_serializer(spaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        space = serializer.save()
        serialized_space = self.get_serializer(space)
        return Response(serialized_space.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def partial_update(self, request, **kwargs):
        """Partial update the connected user."""
        return self.update(request, partial=True, **kwargs)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except SpaceError.DeleteError:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response(status=status.HTTP_204_NO_CONTENT)
