from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ips_app_old.domain.models.node import Node, NodeStatus


class NodeHTTP(ABC):
    @abstractmethod
    async def add_node(
        self,
        device_id: str,
        name: str,
        description: str = "",
    ) -> Node:
        """Add a new node registration."""
        ...

    @abstractmethod
    async def get_node(self, node_id: Any) -> Node:
        """Get a node by its database ID."""
        ...

    @abstractmethod
    async def get_node_by_device_id(self, device_id: str) -> Node:
        """Get a node by its device ID."""
        ...

    @abstractmethod
    async def get_nodes(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
    ) -> Tuple[List[Node], int]:
        """Get nodes with pagination and filtering."""
        ...

    @abstractmethod
    async def set_node_info(
        self,
        node_id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Node:
        """Update a node's basic information."""
        ...

    @abstractmethod
    async def set_node_status(
        self,
        node_id: Any,
        status: NodeStatus,
        updated_by: Optional[Any] = None,
    ) -> Node:
        """Update a node's lifecycle status."""
        ...

    @abstractmethod
    async def set_node_preferences(self, node_id: Any, preferences: bytes) -> Node:
        """Update a node's preferences."""
        ...

    @abstractmethod
    async def remove_node(self, node_id: Any) -> str:
        """Remove a node registration."""
        ...

    @abstractmethod
    async def register_node_connection(
        self,
        device_id: str,
        connection: Any,
    ) -> None:
        """Register an active node control connection."""
        ...

    @abstractmethod
    async def unregister_node_connection(self, device_id: str) -> None:
        """Unregister an active node control connection."""
        ...

    @abstractmethod
    async def is_node_registered(self, device_id: str) -> bool:
        """Check whether a node has an active control connection."""
        ...

    @abstractmethod
    async def get_registered_nodes(self) -> List[str]:
        """Get device IDs with active control connections."""
        ...

    @abstractmethod
    async def restart_node(self, device_id: str) -> None:
        """Request a connected node device restart."""
        ...

    @abstractmethod
    async def add_ranging_record(
        self,
        source_node_device_id: Optional[str],
        target_node_device_id: Optional[str],
        distance: Optional[float],
        recorded_at: datetime,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a ranging time-series record reported through HTTP."""
        ...

    @abstractmethod
    async def add_ranging_record_by_pan_ids(
        self,
        reported_by_device_id: str,
        source_pan_id: int,
        destination_pan_id: int,
        distance: Optional[float],
    ) -> None:
        """Add a ranging time-series record reported by a websocket node."""
        ...
