from rest_framework.viewsets import GenericViewSet

from django_napse.auth.models import NapseAPIKey
from django_napse.core.models import NapseSpace
from django_napse.utils.errors import APIError


class CustomViewSet(GenericViewSet):
    def get_api_key(self, request):
        try:
            return NapseAPIKey.objects.get_from_key(request.META["HTTP_AUTHORIZATION"].split()[1])
        except NapseAPIKey.DoesNotExist as e:
            raise APIError.InvalidAPIKey() from e
        except KeyError as e:
            raise APIError.NoAPIKey() from e

    def space(self, request):
        return NapseSpace.objects.get(uuid=request.query_params["space"])
