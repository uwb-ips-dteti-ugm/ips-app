from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional

from ips_app.domain.models.position import PositionRecord


class PositionUsecase(ABC):
    @abstractmethod
    async def compute_and_store_tag_position(
        self,
        tag_node_id: Any,
        tag_height: float,
    ) -> Optional[PositionRecord]:
        """Trilaterates the tag's current (x, y) from its latest distance to
        each fixed anchor in its network, stores the result, and returns it.
        Returns None if fewer than 3 anchors have a recent reading (no fix)."""
        ...

    @abstractmethod
    async def get_position_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        tag_node_id: Optional[Any] = None,
    ) -> List[PositionRecord]: ...

    @abstractmethod
    async def get_latest_position_record(
        self,
        network_id: Optional[Any] = None,
        tag_node_id: Optional[Any] = None,
    ) -> Optional[PositionRecord]: ...
