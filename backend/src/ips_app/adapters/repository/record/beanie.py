from datetime import datetime
from typing import Any, Dict, List, Optional

from ips_app.adapters.repository.record.beanie_model import RecordDocument
from ips_app.domain.models.exception import (
    DomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.record import (
    Record,
    RecordData,
    RecordDataLabel,
)
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.repository.record import (
    RecordIntervalField,
    RecordRepository,
)
from ips_app.utils.validator import validate_record_data, validate_record_interval


class BeanieRecordRepository(RecordRepository):
    def __init__(self, log: GenericLogging):
        self.log = log
        self.tag_class = "BeanieRecordRepository"

    async def create_record(
        self,
        label: RecordDataLabel,
        data: RecordData,
        recorded_at: datetime,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.create_record"
        session = kwargs.get("session")
        try:
            validate_record_data(label, data)
            doc = RecordDocument(
                label=label,
                data=data,
                metadata=metadata or {},
                recorded_at=recorded_at,
            )
            await doc.insert(session=session)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to create record",
                {"error": str(e), "label": str(label)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_records_by_interval(
        self,
        label: RecordDataLabel,
        interval_field: RecordIntervalField,
        start: datetime,
        end: datetime,
        **kwargs: Any,
    ) -> List[Record]:
        tag = f"{self.tag_class}.read_records_by_interval"
        session = kwargs.get("session")
        try:
            query_filter = self._build_interval_filter(
                label=label,
                interval_field=interval_field,
                start=start,
                end=end,
            )
            docs = (
                await RecordDocument.find(query_filter, session=session)
                .sort(interval_field)
                .to_list()
            )
            return [doc.to_domain() for doc in docs]
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read records by interval",
                {
                    "error": str(e),
                    "label": str(label),
                    "interval_field": str(interval_field),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def delete_records_by_interval(
        self,
        label: RecordDataLabel,
        interval_field: RecordIntervalField,
        start: datetime,
        end: datetime,
        **kwargs: Any,
    ) -> int:
        tag = f"{self.tag_class}.delete_records_by_interval"
        session = kwargs.get("session")
        try:
            query_filter = self._build_interval_filter(
                label=label,
                interval_field=interval_field,
                start=start,
                end=end,
            )
            result = await RecordDocument.get_motor_collection().delete_many(
                query_filter,
                session=session,
            )
            return result.deleted_count
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to delete records by interval",
                {
                    "error": str(e),
                    "label": str(label),
                    "interval_field": str(interval_field),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    def _build_interval_filter(
        self,
        label: RecordDataLabel,
        interval_field: RecordIntervalField,
        start: datetime,
        end: datetime,
    ) -> Dict[str, Any]:
        validate_record_interval(interval_field, start, end)
        return {
            "label": label,
            interval_field: {
                "$gte": start,
                "$lte": end,
            },
        }
