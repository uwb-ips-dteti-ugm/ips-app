from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Tuple, Any, Dict
from ips_app_old.domain.models.node import Node


class NodeRepositoryPort(ABC):
    @abstractmethod
    async def create_node(
        self,
        dev_id: str,
        type: str,
        name: str = "Unknown Node",
        description: str = "",
        preferences: Optional[Dict[str, Any]] = None,
        connected: bool = False,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> Node:
        """Create a newly discovered node. New nodes are unapproved by default."""
        ...

    @abstractmethod
    async def read_node_by_id(self, id: Any, **kwargs: Any) -> Optional[Node]:
        """Read a node by its MongoDB ID."""
        ...

    @abstractmethod
    async def read_node_by_dev_id(self, dev_id: str, **kwargs: Any) -> Optional[Node]:
        """Read a node by its unique device/manufacturer ID."""
        ...

    @abstractmethod
    async def read_nodes_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        type: Optional[str] = None,
        connected: Optional[bool] = None,
        approved: Optional[bool] = None,
        **kwargs: Any,
    ) -> Tuple[List[Node], int]:
        """Read nodes with pagination, search, and common IPS-node filters."""
        ...

    @abstractmethod
    async def update_node_info_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update node user-facing information and optional device type."""
        ...

    @abstractmethod
    async def update_node_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update node preferences JSON data."""
        ...

    @abstractmethod
    async def update_node_connected_by_id(
        self,
        id: Any,
        connected: bool,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update node connection state by MongoDB ID."""
        ...

    @abstractmethod
    async def update_node_connected_by_dev_id(
        self,
        dev_id: str,
        connected: bool,
        **kwargs: Any,
    ) -> None:
        """Update node connection state by device/manufacturer ID."""
        ...

    @abstractmethod
    async def approve_node_by_id(
        self,
        id: Any,
        approved_by: Any,
        approved_at: Optional[datetime] = None,
        **kwargs: Any,
    ) -> None:
        """Approve a discovered node after user verification."""
        ...

    @abstractmethod
    async def revoke_node_approval_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Remove node approval state."""
        ...

    @abstractmethod
    async def delete_node_by_id(self, id: Any, **kwargs: Any) -> None:
        """Delete a node by its MongoDB ID."""
        ...
