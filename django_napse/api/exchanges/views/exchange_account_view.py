from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from django_napse.api.custom_permissions import HasMasterKey
from django_napse.api.custom_viewset import CustomViewSet
from django_napse.api.exchanges.serializers.exchange_account_detail_serializer import ExchangeAccountDetailSerializer
from django_napse.api.exchanges.serializers.exchange_account_serializer import ExchangeAccountSerializer
from django_napse.core.models import Exchange, ExchangeAccount
from django_napse.utils.constants import EXCHANGES

if TYPE_CHECKING:
    from django.db.models.query import Queryset
    from rest_framework import serializers
    from rest_framework.request import Request


class ExchangeAccountView(CustomViewSet):
    """Define endpoints for ExchangeAccount."""

    permission_classes: ClassVar = [HasMasterKey]
    serializer_class = ExchangeAccountSerializer

    def get_object(self) -> ExchangeAccount:
        """Get the ExchangeAccount instance for a detail endpoint."""
        return self.get_queryset().get(uuid=self.kwargs["pk"])

    def get_queryset(self) -> Queryset:
        """Get all ExchangeAccount instances."""
        return ExchangeAccount.objects.all()

    def get_serializer_class(self) -> serializers.Serializer:
        """Get the correct serializer for the action."""
        actions: dict = {
            "list": ExchangeAccountSerializer,
            "retrieve": ExchangeAccountDetailSerializer,
        }
        result = actions.get(self.action)
        return result if result else super().get_serializer_class()

    def list(self, request: Request) -> None:  # noqa: ARG002
        """List all ExchangeAccount instances."""
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, pk: int | str | None = None) -> None:  # noqa: ARG002
        """Return the detail info of the given ExchangeAccount."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request: Request) -> None:
        """Create an ExchangeAccount instance."""
        if "name" not in request.data:
            return Response({"error": "Missing name"}, status=status.HTTP_400_BAD_REQUEST)
        if "exchange" not in request.data:
            return Response({"error": "Missing exchange"}, status=status.HTTP_400_BAD_REQUEST)
        if "testing" not in request.data:
            return Response({"error": "Missing testing"}, status=status.HTTP_400_BAD_REQUEST)

        # TODO (Xénépix) : Rework the following part to use a serializer. # noqa
        exchange = Exchange.objects.get(name=request.data["exchange"])
        exchange_account = ExchangeAccount.objects.create(
            exchange=exchange,
            name=request.data["name"],
            testing=request.data["testing"],
            description=request.data.get("description", ""),
        )
        serializer = self.get_serializer(exchange_account)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request: Request, pk: int | str | None = None) -> None:  # noqa: ARG002
        """Destroy an ExchangeAccount instance."""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request: Request, pk: int | str | None = None) -> None:  # noqa: ARG002
        """Patch an ExchangeAccount instance."""
        instance = self.get_object()
        if "name" in request.data:
            instance.name = request.data["name"]
        if "description" in request.data:
            instance.description = request.data["description"]
        # TODO (Xénépix) : Rework the following part to use a serializer. # noqa

        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def possible_exchanges(self, request: Request) -> None:  # noqa: ARG002
        """Return the list of possible Exchange to build the ExchangeAccount."""
        return Response(list(EXCHANGES), status=status.HTTP_200_OK)
