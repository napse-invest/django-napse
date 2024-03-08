from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.viewsets import GenericViewSet

from django_napse.auth.models import NapseAPIKey
from django_napse.core.models import Space
from django_napse.utils.errors import APIError

if TYPE_CHECKING:
    from rest_framework.request import Request


class CustomViewSet(GenericViewSet):
    """Base of all ViewSets."""

    def get_api_key(self, request: Request) -> NapseAPIKey:
        """Return the api key from the request."""
        try:
            return NapseAPIKey.objects.get_from_key(request.META["HTTP_AUTHORIZATION"].split()[1])
        except NapseAPIKey.DoesNotExist as e:
            raise APIError.InvalidAPIKey from e
        except KeyError as e:
            raise APIError.NoAPIKey from e

    def get_space(self, request: Request) -> Space | None:
        """Return the space from the request."""
        try:
            return Space.objects.get(uuid=request.query_params["space"])
        except Space.DoesNotExist:
            return None
