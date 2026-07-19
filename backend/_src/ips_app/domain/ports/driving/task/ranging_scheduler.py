from abc import ABC, abstractmethod
from typing import Optional

from ips_app.domain.models.ranging import RangingNodePair


class RangingSchedulerTask(ABC):
    @abstractmethod
    async def refresh_registered_nodes(self) -> None:
        """Refresh the scheduler's eligible registered-node snapshot."""
        ...

    @abstractmethod
    async def get_next_node_pair(self) -> Optional[RangingNodePair]:
        """Get the next network-scoped node pair."""
        ...

    @abstractmethod
    async def listen_ranging(
        self,
        pair: RangingNodePair,
        timeout_uus: int,
    ) -> None:
        """Command a connected node to listen for a ranging request."""
        ...

    @abstractmethod
    async def initiate_ranging(
        self,
        pair: RangingNodePair,
        timeout_uus: int,
    ) -> None:
        """Command a connected node to initiate ranging to a listener."""
        ...
