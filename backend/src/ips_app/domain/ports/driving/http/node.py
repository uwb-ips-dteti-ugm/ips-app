from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.node import Node, NodeStatus


class NodeHTTP(ABC):
    @abstractmethod
    async def add_node(
        self,
        device_id: str,
        name: str,
        description: str = "",
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
        created_by: Optional[Any] = None,
    ) -> Node:
        """Add a new node registration."""
        ...

    @abstractmethod
    async def get_node(self, node_id: Any) -> Node:
        """Get a node by its ID."""
        ...

    @abstractmethod
    async def get_node_by_device_id(self, device_id: str) -> Node:
        """Get a node by its device ID."""
        ...

    @abstractmethod
    async def get_node_by_network_address(
        self,
        network_id: Any,
        address: int,
    ) -> Node:
        """Get a node by its network and UWB address."""
        ...

    @abstractmethod
    async def get_nodes(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
    ) -> Tuple[List[Node], int]:
        """Get nodes with cursor-compatible pagination and filtering."""
        ...

    @abstractmethod
    async def set_node_info(
        self,
        node_id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> Node:
        """Update a node's basic information."""
        ...

    @abstractmethod
    async def set_node_network_assignment(
        self,
        node_id: Any,
        network_id: Optional[Any],
        address: Optional[int],
        updated_by: Optional[Any] = None,
    ) -> Node:
        """Update a node's network assignment."""
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
    async def set_node_preferences(
        self,
        node_id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> Node:
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
    async def add_ranging_record_by_addresses(
        self,
        reported_by_device_id: str,
        pan_id: int,
        source_address: int,
        destination_address: int,
        distance: float,
    ) -> None:
        """Add a ranging record reported by a node using PAN/address data."""
        ...
