from abc import ABC, abstractmethod
from typing import Any, List, Optional


class NodeConnectionUsecase(ABC):
    @abstractmethod
    async def register_connection(
        self,
        device_id: str,
        connection: Any,
        board_variant: Optional[str] = None,
    ) -> None: ...

    @abstractmethod
    async def unregister_connection(
        self,
        device_id: str,
        connection: Optional[Any] = None,
    ) -> None: ...

    @abstractmethod
    async def is_connected(self, device_id: str) -> bool: ...

    @abstractmethod
    async def get_connected_device_ids(self) -> List[str]: ...

    @abstractmethod
    async def restart_node(self, device_id: str) -> None: ...
