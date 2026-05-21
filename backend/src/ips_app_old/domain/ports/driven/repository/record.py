from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from ips_app_old.domain.models.record import Record, RecordData, RecordDataLabel


RecordIntervalField = Literal["recorded_at", "created_at"]


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
        interval_field: RecordIntervalField,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Record]:
        """Read records by label and recorded/created time interval."""
        ...

    @abstractmethod
    async def delete_records_by_interval(
        self,
        label: RecordDataLabel,
        interval_field: RecordIntervalField,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> int:
        """Delete records by label and recorded/created time interval."""
        ...
