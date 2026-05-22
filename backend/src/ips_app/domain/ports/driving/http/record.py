from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ips_app.domain.models.record import Record, RecordDataLabel


class RecordHTTP(ABC):
    @abstractmethod
    async def get_records_by_interval(
        self,
        label: RecordDataLabel,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> List[Record]:
        """Get records by label and recorded time interval."""
        ...

    @abstractmethod
    async def get_latest_record_by_label(
        self,
        label: RecordDataLabel,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> Optional[Record]:
        """Get the latest record by label and optional node filters."""
        ...

    @abstractmethod
    async def remove_records_by_interval(
        self,
        label: RecordDataLabel,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
    ) -> int:
        """Remove records by label and recorded time interval."""
        ...
