from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional

from ips_app.domain.models.position import PositionRecord


class PositionRepository(ABC):
    @abstractmethod
    async def create_position_record(
        self,
        network_id: Any,
        tag_node_id: Any,
        x: float,
        y: float,
        tag_height: float,
        computed_at: Optional[datetime] = None,
        session: Optional[Any] = None,
    ) -> PositionRecord: ...

    @abstractmethod
    async def read_position_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        tag_node_id: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> List[PositionRecord]: ...

    @abstractmethod
    async def read_latest_position_record(
        self,
        network_id: Optional[Any] = None,
        tag_node_id: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Optional[PositionRecord]: ...
