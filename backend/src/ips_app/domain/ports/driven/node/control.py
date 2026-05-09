from abc import ABC, abstractmethod
from typing import Any, List


class NodeControl(ABC):
    @abstractmethod
    async def register(self, device_id: str, connection: Any) -> None:
        """Register an active node command connection."""
        ...

    @abstractmethod
    async def unregister(self, device_id: str) -> None:
        """Unregister an active node command connection."""
        ...

    @abstractmethod
    async def is_registered(self, device_id: str) -> bool:
        """Check whether a node device currently has an active command channel."""
        ...

    @abstractmethod
    async def get_registered(self) -> list[str]:
        """List device IDs that currently have active command channels."""
        ...

    @abstractmethod
    async def restart(self, device_id: str) -> None:
        """Request a node device restart."""
        ...

    @abstractmethod
    async def listen_ranging(
        self,
        listener_device_id: str,
        initiator_device_id: str,
        listen_for: int,
    ) -> None:
        """Command a node to listen for a ranging request from another node."""
        ...

    @abstractmethod
    async def initiate_ranging(
        self,
        initiator_device_id: str,
        target_device_ids: str,
        wait_for: int,
    ) -> None:
        """Command a node to range against a target node."""
        ...
