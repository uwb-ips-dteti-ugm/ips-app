from datetime import datetime
from typing import Any, Dict, List, Optional

from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.record import Record, RecordData, RecordDataLabel
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.repository.record import (
    RecordIntervalField,
    RecordRepository,
)
from ips_app.domain.ports.driving.http.record import RecordHTTP


class BaseRecordHTTP(RecordHTTP):
    def __init__(self, repo: RecordRepository, log: GenericLogging):
        self.repo = repo
        self.log = log
        self.tag_class = "BaseRecordHTTP"

    async def add_record(
        self,
        label: RecordDataLabel,
        data: RecordData,
        recorded_at: datetime,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        tag = f"{self.tag_class}.add_record"
        try:
            await self.repo.create_record(
                label=label,
                data=data,
                recorded_at=recorded_at,
                metadata=metadata,
            )
            await self.log.info(
                tag,
                "Successfully added record",
                {"label": str(label), "recorded_at": recorded_at.isoformat()},
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add record",
                {"error": str(e), "label": str(label)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_records_by_interval(
        self,
        label: RecordDataLabel,
        interval_field: RecordIntervalField,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> List[Record]:
        tag = f"{self.tag_class}.get_records_by_interval"
        try:
            records = await self.repo.read_records_by_interval(
                label=label,
                interval_field=interval_field,
                start=start,
                end=end,
                source_node_device_ids=source_node_device_ids,
                target_node_device_ids=target_node_device_ids,
            )
            await self.log.info(
                tag,
                "Successfully fetched records by interval",
                {
                    "label": str(label),
                    "interval_field": str(interval_field),
                    "count": len(records),
                },
            )
            return records
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get records by interval",
                {
                    "error": str(e),
                    "label": str(label),
                    "interval_field": str(interval_field),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_records_by_interval(
        self,
        label: RecordDataLabel,
        interval_field: RecordIntervalField,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
    ) -> int:
        tag = f"{self.tag_class}.remove_records_by_interval"
        try:
            deleted_count = await self.repo.delete_records_by_interval(
                label=label,
                interval_field=interval_field,
                start=start,
                end=end,
                source_node_device_ids=source_node_device_ids,
            )
            await self.log.info(
                tag,
                "Successfully removed records by interval",
                {
                    "label": str(label),
                    "interval_field": str(interval_field),
                    "deleted_count": deleted_count,
                },
            )
            return deleted_count
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove records by interval",
                {
                    "error": str(e),
                    "label": str(label),
                    "interval_field": str(interval_field),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
            )
            raise UnexpectedDomainException(str(e)) from e
