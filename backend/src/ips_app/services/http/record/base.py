from datetime import datetime
from typing import List, Optional

from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.record import Record, RecordDataLabel
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.record import RecordRepository
from ips_app.domain.ports.driving.http.record import RecordHTTP


class BaseRecordHTTP(RecordHTTP):
    def __init__(self, repo: RecordRepository, log: LeveledLogging):
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def get_records_by_interval(
        self,
        label: RecordDataLabel,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> List[Record]:
        tag = f"{self.tag_class}.get_records_by_interval"
        try:
            records = await self.repo.read_records_by_interval(
                label=label,
                start=start,
                end=end,
                source_node_device_ids=source_node_device_ids,
                target_node_device_ids=target_node_device_ids,
            )
            await self.log.info(
                tag,
                "Successfully fetched records by interval",
                {"label": str(label), "count": len(records)},
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
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_records_by_interval(
        self,
        label: RecordDataLabel,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
    ) -> int:
        tag = f"{self.tag_class}.remove_records_by_interval"
        try:
            deleted_count = await self.repo.delete_records_by_interval(
                label=label,
                start=start,
                end=end,
                source_node_device_ids=source_node_device_ids,
            )
            await self.log.info(
                tag,
                "Successfully removed records by interval",
                {"label": str(label), "deleted_count": deleted_count},
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
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
            )
            raise UnexpectedDomainException(str(e)) from e
