from abc import ABC, abstractmethod
from typing import Any


class NodeControl(ABC):
    """Control active node command connections."""

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
        pan_id: int,
        listener_address: int,
        initiator_address: int,
        timeout_uus: int,
    ) -> None:
        """Command a connected node to listen on a PAN for an initiator address."""
        ...

    @abstractmethod
    async def initiate_ranging(
        self,
        device_id: str,
        pan_id: int,
        initiator_address: int,
        listener_address: int,
        timeout_uus: int,
    ) -> None:
        """Command a connected node to initiate ranging to a listener address."""
        ...
