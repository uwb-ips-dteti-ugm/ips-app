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
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
        board_variant: Optional[str] = None,
        created_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def read_node_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def read_node_by_device_id(
        self,
        device_id: str,
        session: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def read_node_by_network_id_and_address(
        self,
        network_id: Any,
        address: int,
        session: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def read_nodes_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        is_online: Optional[bool] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[Node], int]: ...

    @abstractmethod
    async def update_node_info_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def update_node_network_assignment_by_id(
        self,
        id: Any,
        network_id: Optional[Any],
        address: Optional[int],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def update_node_status_by_id(
        self,
        id: Any,
        status: NodeStatus,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def update_node_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def update_node_last_seen_at_by_device_id(
        self,
        device_id: str,
        session: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def update_node_last_connected_at_by_device_id(
        self,
        device_id: str,
        board_variant: Optional[str] = None,
        session: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def update_node_last_disconnected_at_by_device_id(
        self,
        device_id: str,
        session: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def delete_node_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> None: ...
