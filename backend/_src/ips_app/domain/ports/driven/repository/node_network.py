from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from ips_app.domain.models.node_network import NodeNetwork


class NodeNetworkRepository(ABC):
    @abstractmethod
    async def create_node_network(
        self,
        pan_id: int,
        name: str,
        description: str = "",
        created_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> NodeNetwork:
        """Create a node network."""
        ...

    @abstractmethod
    async def read_node_network_by_id(
        self,
        id: Any,
        **kwargs: Any,
    ) -> NodeNetwork:
        """Read a node network by its ID."""
        ...

    @abstractmethod
    async def read_node_network_by_pan_id(
        self,
        pan_id: int,
        **kwargs: Any,
    ) -> NodeNetwork:
        """Read a node network by its UWB PAN ID."""
        ...

    @abstractmethod
    async def read_node_networks_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List[NodeNetwork], int]:
        """Read node networks with pagination and search."""
        ...

    @abstractmethod
    async def update_node_network_by_id(
        self,
        id: Any,
        pan_id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Update a node network."""
        ...

    @abstractmethod
    async def delete_node_network_by_id(self, id: Any, **kwargs: Any) -> None:
        """Delete a node network by its ID."""
        ...
