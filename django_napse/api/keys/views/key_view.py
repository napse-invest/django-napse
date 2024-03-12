from django.db.transaction import atomic
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from django_napse.api.custom_permissions import HasAPIKey, HasMasterKey
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.keys.serializers import NapseAPIKeySerializer
from django_napse.api.keys.serializers.key import NapseAPIKeySpaceSerializer
from django_napse.auth.models import NapseAPIKey
from django_napse.utils.constants import PERMISSION_TYPES


class KeyView(CustomViewSet):
    permission_classes = [HasMasterKey]
    serializer_class = NapseAPIKeySerializer

    def get_queryset(self):
        return NapseAPIKey.objects.all()

    def get_object(self):
        return NapseAPIKey.objects.get(prefix=self.kwargs["pk"])

    def get_permissions(self):
        match self.action:
            case "connect" | "possible_permissions":
                return [HasAPIKey()]
            case "retrieve":
                return [HasAPIKey()]
            case _:
                return super().get_permissions()

    def create(self, request):
        if "name" not in request.data:
            return Response({"error": "Missing name"}, status=status.HTTP_400_BAD_REQUEST)

        _, key = NapseAPIKey.objects.create_key(name=request.data["name"], description=request.data.get("description", ""))

        return Response({"key": key}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        key = self.get_object()
        if "space" not in request.query_params:
            serializer = NapseAPIKeySerializer(key)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = NapseAPIKeySpaceSerializer(
            instance=key,
            context={
                "space": request.query_params["space"],
            },
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        keys = self.get_queryset()
        if "space" not in request.query_params:
            serializer = NapseAPIKeySerializer(keys, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = NapseAPIKeySpaceSerializer(
            keys,
            many=True,
            context={
                "space": request.query_params["space"],
            },
        )
        data = {"keys": []}
        for key in serializer.data:
            if key["permissions"]:
                data["keys"].append(key)
        master_key = NapseAPIKey.objects.get(is_master_key=True)
        serializer = NapseAPIKeySerializer(master_key)
        data["master_key"] = serializer.data
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        key = self.get_object()
        key.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        key = self.get_object()
        with atomic():
            if "name" in request.data:
                key.name = request.data["name"]
            if "description" in request.data:
                key.description = request.data["description"]
            if "permissions" in request.data:
                for permission in key.permissions.filter(space=self.get_space(request)):
                    permission.delete()
                for permission in request.data["permissions"]:
                    key.add_permission(self.get_space(request), permission)
            key.save()
            if request.data.get("revoked", False) and not key.is_master_key:
                key.revoke()
        serializer = NapseAPIKeySerializer(key)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def possible_permissions(self, request):
        return Response(list(PERMISSION_TYPES), status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def connect(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)
