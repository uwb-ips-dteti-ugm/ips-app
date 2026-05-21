from abc import ABC, abstractmethod
from typing import Optional, Tuple


class RangingSchedulerTask(ABC):
    @abstractmethod
    async def refresh_registered_nodes(self) -> None:
        """Refresh the scheduler's eligible registered-node snapshot."""
        ...

    @abstractmethod
    async def get_next_node_pair(self) -> Optional[Tuple[str, str, bool]]:
        """Get the next pair, or None until at least two eligible nodes are connected."""
        ...

    @abstractmethod
    async def listen_ranging(
        self,
        listener_device_id: str,
        initiator_device_id: str,
        listen_for_ms: int,
    ) -> None:
        """Command a connected node to listen for a ranging request."""
        ...

    @abstractmethod
    async def initiate_ranging(
        self,
        initiator_device_id: str,
        target_device_id: str,
        wait_for_ms: int,
    ) -> None:
        """Command a connected node to range against a target node."""
        ...
