from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from ips_app.domain.models.record import (
    Record,
    RecordDataMultilateration,
)


class RecordRepository(ABC):
    @abstractmethod
    async def create_ranging_record(
        self,
        source_node_device_id: str,
        target_node_device_id: str,
        distance: float,
        recorded_at: datetime,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Create a ranging record."""
        ...

    @abstractmethod
    async def read_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Record]:
        """Read ranging records by recorded time interval."""
        ...

    @abstractmethod
    async def read_latest_ranging_record(
        self,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[Record]:
        """Read the latest ranging record."""
        ...

    @abstractmethod
    async def delete_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> int:
        """Delete ranging records by recorded time interval."""
        ...

    @abstractmethod
    async def create_multilateration_record(
        self,
        ref_node_device_id: str,
        coordinates: List[RecordDataMultilateration.MultilaterationCoordinate],
        recorded_at: datetime,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Create a multilateration record."""
        ...

    @abstractmethod
    async def read_multilateration_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Record]:
        """Read multilateration records by recorded time interval."""
        ...

    @abstractmethod
    async def read_latest_multilateration_record(
        self,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[Record]:
        """Read the latest multilateration record."""
        ...

    @abstractmethod
    async def delete_multilateration_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> int:
        """Delete multilateration records by recorded time interval."""
        ...
