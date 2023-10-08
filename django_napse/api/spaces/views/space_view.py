from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django_napse.api.spaces.serializers import SpaceDetailSerializer, SpaceSerializer
from django_napse.core.models import NapseSpace


class SpaceView(GenericViewSet):
    permission_classes = []
    serializer_class = SpaceSerializer

    def get_queryset(self):
        return NapseSpace.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        actions: dict = {
            "list": SpaceSerializer,
            "retrieve": SpaceDetailSerializer,
        }
        result = actions.get(self.action)
        return result if result else super().get_serializer_class()

    def list(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # return Response(None, status=status.HTTP_201_CREATED)
        return Response({"detail": "Method not implemented yet"}, status=status.HTTP_501_NOT_IMPLEMENTED)
