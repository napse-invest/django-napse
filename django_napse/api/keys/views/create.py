from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django_napse.api.keys.serializers import NapseAPIKeySerializer
from django_napse.auth.models import NapseAPIKey


class Key(GenericViewSet):
    def create(self, request):
        if "name" not in request.data:
            return Response({"error": "Missing name"}, status=status.HTTP_400_BAD_REQUEST)
        if "description" not in request.data:
            return Response({"error": "Missing description"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_key = NapseAPIKey.objects.create(name=request.data["name"], description=request.data["description"])
        except IntegrityError:
            return Response({"error": f"Napse API Key (name={request.data['name']}) already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=NapseAPIKeySerializer(new_key).data, status=status.HTTP_200_OK)
