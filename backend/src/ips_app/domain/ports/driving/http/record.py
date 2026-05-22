from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ips_app.domain.models.record import Record


class RecordHTTP(ABC):
    @abstractmethod
    async def get_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> List[Record]:
        """Get ranging records by recorded time interval."""
        ...

    @abstractmethod
    async def get_latest_ranging_record(
        self,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> Optional[Record]:
        """Get the latest ranging record."""
        ...

    @abstractmethod
    async def remove_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> int:
        """Remove ranging records by recorded time interval."""
        ...

    @abstractmethod
    async def get_multilateration_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
    ) -> List[Record]:
        """Get multilateration records by recorded time interval."""
        ...

    @abstractmethod
    async def get_latest_multilateration_record(
        self,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
    ) -> Optional[Record]:
        """Get the latest multilateration record."""
        ...

    @abstractmethod
    async def remove_multilateration_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
    ) -> int:
        """Remove multilateration records by recorded time interval."""
        ...
