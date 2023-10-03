from rest_framework import status
from rest_framework.response import Response

from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.permissions.serializers import PermissionSerializer
from django_napse.auth.models import KeyPermission


class AdminPermission(CustomViewSet):
    def list(self, request):
        space = self.space(request)
        pending_approvals = KeyPermission.objects.filter(space=space, approved=False)
        serializer = PermissionSerializer(data=pending_approvals, many=True)
        serializer.is_valid()

        return Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)
