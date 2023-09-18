from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django_napse.auth.models import KeyPermission, NapseAPIKey
from django_napse.core.models import NapseSpace
from django_napse.utils.constants import PERMISSION_TYPES


class Permission(GenericViewSet):
    def create(self, request):
        if "space_uuid" not in request.data:
            return Response({"error": "Missing space_uuid"}, status=status.HTTP_400_BAD_REQUEST)
        if "api_key" not in request.data:
            return Response({"error": "Missing api_key"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            key = NapseAPIKey.objects.get(napse_API_key=request.data["api_key"])
        except NapseAPIKey.DoesNotExist:
            return Response({"error": f"Napse API Key (name={request.data['api_key']}) does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            space = NapseSpace.objects.get(uuid=request.data["space_uuid"])
        except NapseSpace.DoesNotExist:
            return Response({"error": f"Napse Space (uuid={request.data['space_uuid']}) does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        permission_type = PERMISSION_TYPES.FULL_ACCESS
        KeyPermission.objects.create(key=key, space=space, permission_type=permission_type)
        return Response(status=status.HTTP_204_NO_CONTENT)
