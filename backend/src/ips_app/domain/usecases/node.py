from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.node import Node, NodeStatus


class NodeUsecase(ABC):
    @abstractmethod
    async def create_node(
        self,
        device_id: str,
        name: str,
        description: str = "",
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
        created_by: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def get_node_by_id(self, id: Any) -> Node: ...

    @abstractmethod
    async def get_node_by_device_id(self, device_id: str) -> Node: ...

    @abstractmethod
    async def get_node_by_network_address(
        self,
        network_id: Any,
        address: int,
    ) -> Node: ...

    @abstractmethod
    async def get_nodes(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        is_online: Optional[bool] = None,
    ) -> Tuple[List[Node], int]: ...

    @abstractmethod
    async def update_node_info(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def update_node_network_assignment(
        self,
        id: Any,
        network_id: Optional[Any],
        address: Optional[int],
        updated_by: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def update_node_status(
        self,
        id: Any,
        status: NodeStatus,
        updated_by: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def update_node_preferences(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> Node: ...

    @abstractmethod
    async def delete_node(self, id: Any) -> None: ...
