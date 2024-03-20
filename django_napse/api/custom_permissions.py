from django.forms import ValidationError
from rest_framework.permissions import BasePermission
from rest_framework_api_key.permissions import HasAPIKey  # noqa

from django_napse.core.models import Space
from django_napse.utils.constants import PERMISSION_TYPES
from django_napse.utils.errors import APIError


def check_for_space(request):
    if "space" not in request.query_params:
        raise APIError.MissingSpace()
    try:
        return Space.objects.get(uuid=request.query_params["space"])
    except Space.DoesNotExist as e:
        raise APIError.InvalidSpace() from e
    except ValidationError as e:
        raise APIError.InvalidSpace() from e


class HasAdminPermission(BasePermission):
    def has_permission(self, request, view):
        space = check_for_space(request)

        api_key = view.get_api_key(request)
        if api_key.is_master_key:
            return True
        if any(
            permission.permission_type == PERMISSION_TYPES.ADMIN
            for permission in api_key.permissions.filter(
                space=space,
                approved=True,
                revoked=False,
            )
        ):
            return True
        raise APIError.InvalidPermissions()


class HasFullAccessPermission(BasePermission):
    def has_permission(self, request, view):
        space = check_for_space(request)

        api_key = view.get_api_key(request)
        if api_key.is_master_key:
            return True
        for permission in api_key.permissions.filter(
            space=space,
            approved=True,
            revoked=False,
        ):
            if permission.permission_type in [PERMISSION_TYPES.ADMIN, PERMISSION_TYPES.FULL_ACCESS]:
                return True
        raise APIError.InvalidPermissions()


class HasReadPermission(BasePermission):
    def has_permission(self, request, view):
        space = check_for_space(request)

        api_key = view.get_api_key(request)
        if api_key.is_master_key:
            return True
        for permission in api_key.permissions.filter(
            space=space,
            approved=True,
            revoked=False,
        ):
            if permission.permission_type in [PERMISSION_TYPES.ADMIN, PERMISSION_TYPES.FULL_ACCESS, PERMISSION_TYPES.READ_ONLY]:
                return True
        raise APIError.InvalidPermissions()


class HasSpace(BasePermission):
    def has_permission(self, request, view):
        check_for_space(request)
        return True


class HasMasterKey(BasePermission):
    def has_permission(self, request, view):
        api_key = view.get_api_key(request)
        if api_key.is_master_key:
            return True
        raise APIError.InvalidPermissions()
