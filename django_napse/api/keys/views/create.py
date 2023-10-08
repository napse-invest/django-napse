from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_api_key.models import APIKey


class Key(GenericViewSet):
    permission_classes = []

    def create(self, request):
        if "username" not in request.data:
            return Response({"error": "Missing name"}, status=status.HTTP_400_BAD_REQUEST)
        _, key = APIKey.objects.create_key(name=request.data["username"])
        return Response({"key": key}, status=status.HTTP_201_CREATED)
