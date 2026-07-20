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
        session: Optional[Any] = None,
    ) -> NodeNetwork: ...

    @abstractmethod
    async def read_node_network_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> NodeNetwork: ...

    @abstractmethod
    async def read_node_network_by_pan_id(
        self,
        pan_id: int,
        session: Optional[Any] = None,
    ) -> NodeNetwork: ...

    @abstractmethod
    async def read_node_networks_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[NodeNetwork], int]: ...

    @abstractmethod
    async def update_node_network_by_id(
        self,
        id: Any,
        pan_id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> NodeNetwork: ...

    @abstractmethod
    async def delete_node_network_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> None: ...
