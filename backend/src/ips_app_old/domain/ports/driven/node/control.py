from abc import ABC, abstractmethod
from typing import Any


class ControlNode(ABC):
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
        device_id: str,
        listener_pan_id: int,
        initiator_pan_id: int,
        listen_for_ms: int,
    ) -> None:
        """Command the connected node to listen with listener and initiator PAN IDs."""
        ...

    @abstractmethod
    async def initiate_ranging(
        self,
        device_id: str,
        initiator_pan_id: int,
        listener_pan_id: int,
        wait_for_ms: int,
    ) -> None:
        """Command the connected node to initiate ranging with initiator and listener PAN IDs."""
        ...
