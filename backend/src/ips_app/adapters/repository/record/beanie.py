from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from ips_app.adapters.repository.record.beanie_model import RecordDocument
from ips_app.domain.models.exception import (
    DomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.record import (
    Record,
    RecordData,
    RecordDataLabel,
)
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.record import RecordRepository
from ips_app.utils.validator import validate_ids_list, validate_record_interval


class BeanieRecordRepository(RecordRepository):
    def __init__(self, log: LeveledLogging):
        self.log = log
        self.tag_class = self.__class__.__name__

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
            record = Record(
                label=label,
                data=data,
                metadata=metadata or {},
                recorded_at=recorded_at,
            )
            doc = RecordDocument(
                label=record.label,
                data=record.data,
                metadata=record.metadata,
                recorded_at=record.recorded_at,
            )
            await doc.insert(session=session)
        except DomainException:
            raise
        except ValidationError as e:
            raise ValidatorDomainException(str(e)) from e
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
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Record]:
        tag = f"{self.tag_class}.read_records_by_interval"
        session = kwargs.get("session")
        try:
            query_filter = self._build_interval_filter(
                label=label,
                start=start,
                end=end,
                source_node_device_ids=source_node_device_ids,
                target_node_device_ids=target_node_device_ids,
            )
            docs = (
                await RecordDocument.find(query_filter, session=session)
                .sort("recorded_at")
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
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "source_node_device_ids": source_node_device_ids,
                    "target_node_device_ids": target_node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_latest_record_by_label(
        self,
        label: RecordDataLabel,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[Record]:
        tag = f"{self.tag_class}.read_latest_record_by_label"
        session = kwargs.get("session")
        try:
            query_filter: Dict[str, Any] = {"label": label}
            self._add_node_device_filters(
                query_filter=query_filter,
                label=label,
                source_node_device_ids=source_node_device_ids,
                target_node_device_ids=target_node_device_ids,
            )
            docs = (
                await RecordDocument.find(query_filter, session=session)
                .sort("-recorded_at")
                .limit(1)
                .to_list()
            )
            if not docs:
                return None

            return docs[0].to_domain()
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read latest record by label",
                {
                    "error": str(e),
                    "label": str(label),
                    "source_node_device_ids": source_node_device_ids,
                    "target_node_device_ids": target_node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def delete_records_by_interval(
        self,
        label: RecordDataLabel,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> int:
        tag = f"{self.tag_class}.delete_records_by_interval"
        session = kwargs.get("session")
        try:
            query_filter = self._build_interval_filter(
                label=label,
                start=start,
                end=end,
                source_node_device_ids=source_node_device_ids,
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
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "source_node_device_ids": source_node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    def _build_interval_filter(
        self,
        label: RecordDataLabel,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        validate_record_interval(start, end)
        query_filter: Dict[str, Any] = {
            "label": label,
            "recorded_at": {
                "$gte": start,
                "$lte": end,
            },
        }
        self._add_node_device_filters(
            query_filter=query_filter,
            label=label,
            source_node_device_ids=source_node_device_ids,
            target_node_device_ids=target_node_device_ids,
        )
        return query_filter

    def _add_node_device_filters(
        self,
        query_filter: Dict[str, Any],
        label: RecordDataLabel,
        source_node_device_ids: Optional[List[str]],
        target_node_device_ids: Optional[List[str]] = None,
    ) -> None:
        if source_node_device_ids is not None:
            validate_ids_list(source_node_device_ids, "source_node_device_ids")
            query_filter[self._source_node_device_path(label)] = {
                "$in": source_node_device_ids,
            }

        if target_node_device_ids is not None:
            validate_ids_list(target_node_device_ids, "target_node_device_ids")
            query_filter[self._target_node_device_path(label)] = {
                "$in": target_node_device_ids,
            }

    def _source_node_device_path(self, label: RecordDataLabel) -> str:
        if label == RecordDataLabel.RANGING:
            return "data.source_node_device_id"
        if label == RecordDataLabel.MULTILATERATION:
            return "data.ref_node_device_id"
        return "data.source_node_device_id"

    def _target_node_device_path(self, label: RecordDataLabel) -> str:
        if label == RecordDataLabel.RANGING:
            return "data.target_node_device_id"
        if label == RecordDataLabel.MULTILATERATION:
            return "data.coordinates.node_device_id"
        return "data.target_node_device_id"
