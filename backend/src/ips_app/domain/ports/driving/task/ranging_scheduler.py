from abc import ABC, abstractmethod
from typing import List


class RangingSchedulerTask(ABC):
    @abstractmethod
    async def get_registered_nodes(self) -> List[str]:
        """Get device IDs with active node control connections."""
        ...

    @abstractmethod
    async def listen_ranging(
        self,
        listener_device_id: str,
        initiator_device_id: str,
        listen_for: int,
    ) -> None:
        """Command a connected node to listen for a ranging request."""
        ...

    @abstractmethod
    async def initiate_ranging(
        self,
        initiator_device_id: str,
        target_device_id: str,
        wait_for: int,
    ) -> None:
        """Command a connected node to range against a target node."""
        ...
