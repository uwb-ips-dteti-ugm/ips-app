from abc import ABC, abstractmethod
from typing import Any, List


class NodeControl(ABC):
    @abstractmethod
    async def register(self, device_id: str, connection: Any) -> None: ...

    @abstractmethod
    async def unregister(self, device_id: str, connection: Any = None) -> bool: ...

    @abstractmethod
    async def is_registered(self, device_id: str) -> bool: ...

    @abstractmethod
    async def get_registered(self) -> List[str]: ...

    @abstractmethod
    async def restart(self, device_id: str) -> None: ...

    @abstractmethod
    async def ranging_listen(
        self,
        device_id: str,
        pan_id: int,
        listener_address: int,
        initiator_address: int,
        timeout_uus: int,
    ) -> None: ...

    @abstractmethod
    async def ranging_initiate(
        self,
        device_id: str,
        pan_id: int,
        initiator_address: int,
        listener_address: int,
        timeout_uus: int,
    ) -> None: ...
