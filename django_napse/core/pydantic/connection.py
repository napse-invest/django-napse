from dataclasses import dataclass
from typing import TYPE_CHECKING

from django_napse.core.pydantic.wallet import WalletPydantic

if TYPE_CHECKING:
    from django_napse.core.models.connections.connection import Connection, ConnectionSpecificArgs


@dataclass
class ConnectionDataclass:
    """Reprensents all the data needed to represent a connection without having to query the database after this initial call."""

    connection: "Connection"
    wallet: WalletPydantic
    connection_specific_args: dict[str, "ConnectionSpecificArgs"]
