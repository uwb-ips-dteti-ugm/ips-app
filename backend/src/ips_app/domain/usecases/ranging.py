from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional

from ips_app.domain.models.ranging import RangingRecord


class RangingUsecase(ABC):
    @abstractmethod
    async def report_ranging_measurement(
        self,
        reported_by_device_id: str,
        pan_id: int,
        source_address: int,
        destination_address: int,
        distance: float,
    ) -> RangingRecord: ...

    @abstractmethod
    async def get_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
    ) -> List[RangingRecord]: ...

    @abstractmethod
    async def get_latest_ranging_record(
        self,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
    ) -> Optional[RangingRecord]: ...

    @abstractmethod
    async def delete_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
    ) -> int: ...
