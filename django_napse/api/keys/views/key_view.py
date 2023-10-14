from django.db.transaction import atomic
from rest_framework import status
from rest_framework.response import Response

from django_napse.api.custom_permissions import HasMasterKey
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.keys.serializers import NapseAPIKeySerializer
from django_napse.api.keys.serializers.key import NapseAPIKeySpaceSerializer
from django_napse.auth.models import NapseAPIKey


class Key(CustomViewSet):
    permission_classes = [HasMasterKey]

    def get_queryset(self):
        return NapseAPIKey.objects.all()

    def get_object(self):
        return NapseAPIKey.objects.get(prefix=self.kwargs["pk"])

    def create(self, request):
        if "name" not in request.data:
            return Response({"error": "Missing name"}, status=status.HTTP_400_BAD_REQUEST)

        with atomic():
            _, key = NapseAPIKey.objects.create_key(name=request.data["name"], description=request.data.get("name", ""))

        return Response({"key": key}, status=status.HTTP_201_CREATED)

    def list(self, request):
        keys = self.get_queryset()
        if "space" not in request.query_params:
            serializer = NapseAPIKeySerializer(keys, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = NapseAPIKeySpaceSerializer(keys, many=True, context={"space": request.query_params["space"]})
        data = {"keys": []}
        for key in serializer.data:
            if key["permissions"]:
                data["keys"].append(key)
        master_key = NapseAPIKey.objects.get(is_master_key=True)
        serializer = NapseAPIKeySerializer(master_key)
        data["master_key"] = serializer.data
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        key = self.get_object()
        serializer = NapseAPIKeySerializer(key)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        key = self.get_object()
        key.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        key = self.get_object()
        if "name" in request.data:
            key.name = request.data["name"]
        if "permissions" in request.data:
            key.permissions.all().delete()
            for permission in request.data["permissions"]:
                key.add_permission(self.space, permission)
        key.save()
        serializer = NapseAPIKeySerializer(key)
        return Response(serializer.data, status=status.HTTP_200_OK)
