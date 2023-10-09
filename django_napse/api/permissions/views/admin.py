from rest_framework import status
from rest_framework.response import Response

from django_napse.api.custom_permissions import HasAdminPermission, HasAPIKey, HasSpace
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.permissions.serializers import PermissionSerializer
from django_napse.auth.models import KeyPermission


class AdminPermission(CustomViewSet):
    permission_classes = [HasSpace, HasAPIKey, HasAdminPermission]

    def list(self, request):
        space = self.space(request)
        approved = request.query_params.get("approved", False)
        pending_approvals = KeyPermission.objects.filter(space=space, approved=approved)
        serializer = PermissionSerializer(data=pending_approvals, many=True)
        serializer.is_valid()
        return Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk=None):
        space = self.space(request)

        if "approved" not in request.data:
            error_msg = "approved not in request.data"
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        if "revoque" not in request.data:
            error_msg = "revoque not in request.data"
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

        try:
            permission = KeyPermission.objects.get(space=space, uuid=pk)
        except KeyPermission.DoesNotExist:
            return Response({"error": "Permission not found"}, status=status.HTTP_400_BAD_REQUEST)

        if permission.revoked:
            return Response({"error": "Permission already revoked"}, status=status.HTTP_400_BAD_REQUEST)

        permission.approved = request.data["approved"]
        permission.revoque = request.data["revoque"]
        permission.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
