from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional

from ips_app.domain.models.ranging import RangingRecord


class RangingRepository(ABC):
    @abstractmethod
    async def create_ranging_record(
        self,
        listener_node_id: Any,
        initiator_node_id: Any,
        distance: float,
        recorded_at: Optional[datetime] = None,
        session: Optional[Any] = None,
    ) -> RangingRecord: ...

    @abstractmethod
    async def read_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> List[RangingRecord]: ...

    @abstractmethod
    async def read_latest_ranging_record(
        self,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Optional[RangingRecord]: ...

    @abstractmethod
    async def delete_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> int: ...
