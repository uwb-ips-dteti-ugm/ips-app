from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from ips_app.domain.models.record import Record, RecordData, RecordDataLabel


class RecordRepository(ABC):
    @abstractmethod
    async def create_record(
        self,
        label: RecordDataLabel,
        data: RecordData,
        recorded_at: datetime,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Create a time-series record."""
        ...

    @abstractmethod
    async def read_records_by_interval(
        self,
        label: RecordDataLabel,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Record]:
        """Read records by label and recorded time interval."""
        ...

    @abstractmethod
    async def read_latest_record_by_label(
        self,
        label: RecordDataLabel,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[Record]:
        """Read the latest record by label and optional node filters."""
        ...

    @abstractmethod
    async def delete_records_by_interval(
        self,
        label: RecordDataLabel,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> int:
        """Delete records by label and recorded time interval."""
        ...
