from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ips_app_old.domain.models.record import Record, RecordDataLabel
from ips_app_old.domain.ports.driven.repository.record import RecordIntervalField


class RecordHTTP(ABC):
    @abstractmethod
    async def get_records_by_interval(
        self,
        label: RecordDataLabel,
        interval_field: RecordIntervalField,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> List[Record]:
        """Get records by label and recorded/created time interval."""
        ...

    @abstractmethod
    async def remove_records_by_interval(
        self,
        label: RecordDataLabel,
        interval_field: RecordIntervalField,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
    ) -> int:
        """Remove records by label and recorded/created time interval."""
        ...
