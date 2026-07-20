from abc import ABC, abstractmethod
from typing import Optional

from ips_app.domain.models.ranging import RangingPair


class RangingSchedulerUsecase(ABC):
    @abstractmethod
    async def refresh_registered_nodes(self) -> None: ...

    @abstractmethod
    async def get_next_pair(self) -> Optional[RangingPair]: ...

    @abstractmethod
    async def listen(self, pair: RangingPair, timeout_uus: int) -> None: ...

    @abstractmethod
    async def initiate(self, pair: RangingPair, timeout_uus: int) -> None: ...
