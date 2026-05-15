from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.node import Node, NodeStatus


class NodeRepository(ABC):
    @abstractmethod
    async def create_node(
        self,
        device_id: str,
        name: str,
        description: str = "",
        pan_id: Optional[int] = None,
        network_address: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
        created_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> Node:
        """Create a node registration."""
        ...

    @abstractmethod
    async def read_node_by_id(self, id: Any, **kwargs: Any) -> Node:
        """Read a node by its database ID."""
        ...

    @abstractmethod
    async def read_node_by_device_id(self, device_id: str, **kwargs: Any) -> Node:
        """Read a node by its device ID."""
        ...

    @abstractmethod
    async def read_nodes_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
        network_address: Optional[int] = None,
        **kwargs: Any,
    ) -> Tuple[List[Node], int]:
        """Read nodes with pagination and filtering."""
        ...

    @abstractmethod
    async def update_node_info_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Update node name or description."""
        ...

    @abstractmethod
    async def update_node_status_by_id(
        self,
        id: Any,
        status: NodeStatus,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Update node lifecycle status."""
        ...

    @abstractmethod
    async def update_node_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Update node preferences."""
        ...

    @abstractmethod
    async def update_node_last_seen_at_by_device_id(
        self,
        device_id: str,
        **kwargs: Any,
    ) -> None:
        """Update the last time a node was observed by device ID."""
        ...

    @abstractmethod
    async def update_node_last_connected_at_by_device_id(
        self,
        device_id: str,
        **kwargs: Any,
    ) -> None:
        """Update the last time a node websocket connected by device ID."""
        ...

    @abstractmethod
    async def update_node_last_disconnected_at_by_device_id(
        self,
        device_id: str,
        **kwargs: Any,
    ) -> None:
        """Update the last time a node websocket disconnected by device ID."""
        ...

    @abstractmethod
    async def delete_node_by_id(self, id: Any, **kwargs: Any) -> None:
        """Delete a node registration by database ID."""
        ...
