from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from ips_app.domain.models.node_network import NodeNetwork


class NodeNetworkHTTP(ABC):
    @abstractmethod
    async def add_node_network(
        self,
        pan_id: int,
        name: str,
        description: str = "",
        created_by: Optional[Any] = None,
    ) -> NodeNetwork:
        """Add a node network."""
        ...

    @abstractmethod
    async def get_node_network(self, node_network_id: Any) -> NodeNetwork:
        """Get a node network by its ID."""
        ...

    @abstractmethod
    async def get_node_network_by_pan_id(self, pan_id: int) -> NodeNetwork:
        """Get a node network by its UWB PAN ID."""
        ...

    @abstractmethod
    async def get_node_networks(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[NodeNetwork], int]:
        """Get node networks with cursor-compatible pagination."""
        ...

    @abstractmethod
    async def set_node_network(
        self,
        node_network_id: Any,
        pan_id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> NodeNetwork:
        """Update a node network."""
        ...

    @abstractmethod
    async def remove_node_network(self, node_network_id: Any) -> str:
        """Remove a node network if no node uses it."""
        ...
