from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from django_napse.api.custom_permissions import HasFullAccessPermission, HasMasterKey, HasReadPermission
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.spaces.serializers import SpaceDetailSerializer, SpaceMoneyFlowSerializer, SpaceSerializer
from django_napse.core.models import NapseSpace
from django_napse.utils.constants import EXCHANGE_TICKERS
from django_napse.utils.errors import SpaceError


class SpaceView(CustomViewSet):
    permission_classes = [HasFullAccessPermission]
    serializer_class = SpaceSerializer

    def get_object(self):
        return self.get_queryset().get(uuid=self.kwargs["pk"])

    def get_queryset(self):
        return NapseSpace.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        actions: dict = {
            "list": SpaceSerializer,
            "retrieve": SpaceDetailSerializer,
            "create": SpaceSerializer,
            "update": SpaceSerializer,
            "partial_update": SpaceSerializer,
            "invest": SpaceMoneyFlowSerializer,
            "withdraw": SpaceMoneyFlowSerializer,
        }
        result = actions.get(self.action, None)
        return result if result else super().get_serializer_class()

    def get_permissions(self):
        match self.action:
            case "retrieve":
                return [HasReadPermission()]
            case "list":
                return [HasAPIKey()]
            case "create":
                return [HasMasterKey()]

            case _:
                return super().get_permissions()

    def list(self, request):
        api_key = self.get_api_key(request)
        spaces = NapseSpace.objects.all() if api_key.is_master_key else NapseSpace.objects.filter(permissions__in=api_key.permissions.all())
        serializer = self.get_serializer(spaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        space = serializer.save()
        serialized_space = self.get_serializer(space)
        return Response(serialized_space.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def partial_update(self, request, **kwargs):
        """Partial update the connected user."""
        return self.update(request, partial=True, **kwargs)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except SpaceError.DeleteError:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["GET", "POST"])
    def invest(self, request, pk=None):
        """Endpoint to invest on space.

        GET: Return all {ticker: amount} which can be invested in the space.
        POST: Invest in the space.
        """
        space: NapseSpace = self.get_object()
        if not space.testing:
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

        exchange_name: str = space.exchange_account.exchange.name

        match request.method:
            case "GET":
                possible_investments = [{"ticker": ticker, "amount": 1_000_000} for ticker in EXCHANGE_TICKERS.get(exchange_name)]
                return Response(possible_investments, status=status.HTTP_200_OK)

            case "POST":
                space = self.get_object()
                if not space.testing:
                    error_msg: str = "Investing in real is not allowed yet."
                    return Response(error_msg, status=status.HTTP_403_FORBIDDEN)
                serializer = self.get_serializer(data=request.data, instance=space, side="INVEST")
                serializer.is_valid(raise_exception=True)
                serializer.save()

            case _:
                return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET", "POST"])
    def withdraw(self, request, pk=None):
        """Endpoint to withdraw on space.

        GET: Return all {ticker: amount} which can be withdrawn in the space.
        POST: Withdraw from the space.
        """
        space: NapseSpace = self.get_object()
        if not space.testing:
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

        match request.method:
            case "GET":
                return Response(status=status.HTTP_200_OK)
            case "POST":
                return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
            case _:
                return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
