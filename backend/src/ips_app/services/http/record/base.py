from datetime import datetime
from typing import List, Optional

from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.record import Record
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.record import RecordRepository
from ips_app.domain.ports.driving.http.record import RecordHTTP


class BaseRecordHTTP(RecordHTTP):
    def __init__(self, repo: RecordRepository, log: LeveledLogging):
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def get_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> List[Record]:
        tag = f"{self.tag_class}.get_ranging_records_by_interval"
        try:
            records = await self.repo.read_ranging_records_by_interval(
                start=start,
                end=end,
                source_node_device_ids=source_node_device_ids,
                target_node_device_ids=target_node_device_ids,
            )
            await self.log.info(
                tag,
                "Successfully fetched ranging records by interval",
                {"count": len(records)},
            )
            return records
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get ranging records by interval",
                {
                    "error": str(e),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "source_node_device_ids": source_node_device_ids,
                    "target_node_device_ids": target_node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_latest_ranging_record(
        self,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> Optional[Record]:
        tag = f"{self.tag_class}.get_latest_ranging_record"
        try:
            record = await self.repo.read_latest_ranging_record(
                source_node_device_ids=source_node_device_ids,
                target_node_device_ids=target_node_device_ids,
            )
            await self.log.info(
                tag,
                "Successfully fetched latest ranging record",
                {"found": record is not None},
            )
            return record
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get latest ranging record",
                {
                    "error": str(e),
                    "source_node_device_ids": source_node_device_ids,
                    "target_node_device_ids": target_node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> int:
        tag = f"{self.tag_class}.remove_ranging_records_by_interval"
        try:
            deleted_count = await self.repo.delete_ranging_records_by_interval(
                start=start,
                end=end,
                source_node_device_ids=source_node_device_ids,
                target_node_device_ids=target_node_device_ids,
            )
            await self.log.info(
                tag,
                "Successfully removed ranging records by interval",
                {"deleted_count": deleted_count},
            )
            return deleted_count
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove ranging records by interval",
                {
                    "error": str(e),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "source_node_device_ids": source_node_device_ids,
                    "target_node_device_ids": target_node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_multilateration_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
    ) -> List[Record]:
        tag = f"{self.tag_class}.get_multilateration_records_by_interval"
        try:
            records = await self.repo.read_multilateration_records_by_interval(
                start=start,
                end=end,
                ref_node_device_ids=ref_node_device_ids,
                node_device_ids=node_device_ids,
            )
            await self.log.info(
                tag,
                "Successfully fetched multilateration records by interval",
                {"count": len(records)},
            )
            return records
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get multilateration records by interval",
                {
                    "error": str(e),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "ref_node_device_ids": ref_node_device_ids,
                    "node_device_ids": node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_latest_multilateration_record(
        self,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
    ) -> Optional[Record]:
        tag = f"{self.tag_class}.get_latest_multilateration_record"
        try:
            record = await self.repo.read_latest_multilateration_record(
                ref_node_device_ids=ref_node_device_ids,
                node_device_ids=node_device_ids,
            )
            await self.log.info(
                tag,
                "Successfully fetched latest multilateration record",
                {"found": record is not None},
            )
            return record
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get latest multilateration record",
                {
                    "error": str(e),
                    "ref_node_device_ids": ref_node_device_ids,
                    "node_device_ids": node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_multilateration_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
    ) -> int:
        tag = f"{self.tag_class}.remove_multilateration_records_by_interval"
        try:
            deleted_count = (
                await self.repo.delete_multilateration_records_by_interval(
                    start=start,
                    end=end,
                    ref_node_device_ids=ref_node_device_ids,
                    node_device_ids=node_device_ids,
                )
            )
            await self.log.info(
                tag,
                "Successfully removed multilateration records by interval",
                {"deleted_count": deleted_count},
            )
            return deleted_count
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove multilateration records by interval",
                {
                    "error": str(e),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "ref_node_device_ids": ref_node_device_ids,
                    "node_device_ids": node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e
