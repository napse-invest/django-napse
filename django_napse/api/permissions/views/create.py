from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from django_napse.api.custom_permissions import HasSpace
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.auth.models import KeyPermission
from django_napse.utils.constants import PERMISSION_TYPES


class Permission(CustomViewSet):
    permission_classes = [HasAPIKey, HasSpace]

    def create(self, request):
        space = self.space(request)

        if "permission_type" not in request.data:
            return Response({"error": "Missing permission_type"}, status=status.HTTP_400_BAD_REQUEST)

        if request.data["permission_type"] not in PERMISSION_TYPES:
            return Response({"error": f"Permission type ({request.data['permission_type']}) does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            KeyPermission.objects.create(key=self.get_api_key(request), space=space, permission_type=request.data["permission_type"])
        except IntegrityError:
            return Response(
                {"error": f"Permission {request.data['permission_type']} already exists for this key and space."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_201_CREATED)
