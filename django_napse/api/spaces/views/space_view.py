from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from django_napse.api.custom_permissions import HasFullAccessPermission, HasMasterKey, HasReadPermission
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.spaces.serializers import SpaceDetailSerializer, SpaceMoneyFlowSerializer, SpaceSerializer, serializers
from django_napse.core.models import Space
from django_napse.utils.constants import EXCHANGE_TICKERS
from django_napse.utils.errors import SpaceError

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models import QuerySet
    from rest_framework.request import Request


class SpaceView(CustomViewSet):
    """Endpoints for Spaces."""

    permission_classes: ClassVar[list] = [HasFullAccessPermission]
    serializer_class = SpaceSerializer

    def get_object(self) -> Space:
        """Return the space instance for detail endpoint."""
        return self.get_queryset().get(uuid=self.kwargs["pk"])

    def get_queryset(self) -> QuerySet[Space]:
        """Return all spaces instances."""
        return Space.objects.all()

    def get_serializer_class(self) -> serializers.Serializer:
        """Return the serializer class for each action."""
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

    def get_permissions(self) -> list:
        """Return permissions for each action."""
        match self.action:
            case "retrieve":
                return [HasReadPermission()]
            case "list":
                return [HasAPIKey()]
            case "create":
                return [HasMasterKey()]

            case _:
                return super().get_permissions()

    def list(self, request: Request) -> None:
        """Return all available spaces (depending of the keys permissions)."""
        api_key = self.get_api_key(request)
        spaces = Space.objects.all() if api_key.is_master_key else Space.objects.filter(permissions__in=api_key.permissions.all())
        serializer = self.get_serializer(spaces, many=True)
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(
        self,
        request: Request,  # noqa: ARG002
        pk: int | str | UUID | None = None,  # noqa: ARG002
    ) -> None:
        """Return the detail info of the given space."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request: Request) -> None:
        """Create a space."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        space = serializer.save()
        serialized_space = self.get_serializer(space)
        return Response(serialized_space.data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, **kwargs: dict[str, any]) -> None:
        """Update the given space."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def partial_update(self, request: Request, **kwargs: dict[str, any]) -> None:
        """Update the given space."""
        return self.update(request, partial=True, **kwargs)

    def delete(
        self,
        request: Request,  # noqa: ARG002
        pk: int | str | UUID | None = None,  # noqa: ARG002
    ) -> None:
        """Delete the given space."""
        instance = self.get_object()
        try:
            instance.delete()
        except SpaceError.DeleteError:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["GET", "POST"])
    def invest(
        self,
        request: Request,
        pk: int | str | UUID | None = None,  # noqa: ARG002
    ) -> None:
        """Endpoint to invest on space.

        GET: Return all {ticker: amount} which can be invested in the space.
        POST: Invest in the space.
        """
        space: Space = self.get_object()
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
    def withdraw(
        self,
        request: Request,
        pk: int | str | UUID | None = None,  # noqa: ARG002
    ) -> None:
        """Endpoint to withdraw on space.

        GET: Return all {ticker: amount} which can be withdrawn in the space.
        POST: Withdraw from the space.
        """
        space: Space = self.get_object()
        if not space.testing:
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

        match request.method:
            case "GET":
                return Response(status=status.HTTP_200_OK)
            case "POST":
                return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
            case _:
                return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
