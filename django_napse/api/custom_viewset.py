from rest_framework.viewsets import GenericViewSet
from rest_framework_api_key.models import APIKey

from django_napse.core.models import NapseSpace


class CustomViewSet(GenericViewSet):
    def get_api_key(self, request):
        return APIKey.objects.get_from_key(request.META["HTTP_AUTHORIZATION"].split()[1])

    def space(self, request):
        return NapseSpace.objects.get(uuid=request.query_params["space"])
