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
    RecordDataMultilateration,
    RecordDataRanging,
)
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.record import RecordRepository
from ips_app.utils.validator import (
    validate_ids_list,
    validate_non_empty_string,
    validate_non_negative_float,
    validate_record_interval,
)


RANGING_SOURCE_NODE_FIELD = "data.source_node_device_id"
RANGING_TARGET_NODE_FIELD = "data.target_node_device_id"
MULTILATERATION_REF_NODE_FIELD = "data.ref_node_device_id"
MULTILATERATION_NODE_FIELD = "data.coordinates.node_device_id"


class BeanieRecordRepository(RecordRepository):
    def __init__(self, log: LeveledLogging):
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_ranging_record(
        self,
        source_node_device_id: str,
        target_node_device_id: str,
        distance: float,
        recorded_at: datetime,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.create_ranging_record"
        try:
            validate_non_empty_string(source_node_device_id, "source_node_device_id")
            validate_non_empty_string(target_node_device_id, "target_node_device_id")
            validate_non_negative_float(distance, "distance")
            await self._create_record(
                label=RecordDataLabel.RANGING,
                data=RecordDataRanging(
                    source_node_device_id=source_node_device_id,
                    target_node_device_id=target_node_device_id,
                    distance=distance,
                ),
                recorded_at=recorded_at,
                metadata=metadata,
                session=kwargs.get("session"),
            )
        except DomainException:
            raise
        except ValidationError as e:
            raise ValidatorDomainException(str(e)) from e
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to create ranging record",
                {
                    "error": str(e),
                    "source_node_device_id": source_node_device_id,
                    "target_node_device_id": target_node_device_id,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Record]:
        tag = f"{self.tag_class}.read_ranging_records_by_interval"
        try:
            query_filter = self._build_ranging_filter(
                start=start,
                end=end,
                source_node_device_ids=source_node_device_ids,
                target_node_device_ids=target_node_device_ids,
            )
            return await self._read_records(query_filter, kwargs.get("session"))
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read ranging records by interval",
                {
                    "error": str(e),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "source_node_device_ids": source_node_device_ids,
                    "target_node_device_ids": target_node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_latest_ranging_record(
        self,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[Record]:
        tag = f"{self.tag_class}.read_latest_ranging_record"
        try:
            query_filter = self._build_ranging_filter(
                source_node_device_ids=source_node_device_ids,
                target_node_device_ids=target_node_device_ids,
            )
            return await self._read_latest_record(query_filter, kwargs.get("session"))
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read latest ranging record",
                {
                    "error": str(e),
                    "source_node_device_ids": source_node_device_ids,
                    "target_node_device_ids": target_node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def delete_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> int:
        tag = f"{self.tag_class}.delete_ranging_records_by_interval"
        try:
            query_filter = self._build_ranging_filter(
                start=start,
                end=end,
                source_node_device_ids=source_node_device_ids,
                target_node_device_ids=target_node_device_ids,
            )
            return await self._delete_records(query_filter, kwargs.get("session"))
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to delete ranging records by interval",
                {
                    "error": str(e),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "source_node_device_ids": source_node_device_ids,
                    "target_node_device_ids": target_node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def create_multilateration_record(
        self,
        ref_node_device_id: str,
        coordinates: List[RecordDataMultilateration.MultilaterationCoordinate],
        recorded_at: datetime,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.create_multilateration_record"
        try:
            validate_non_empty_string(ref_node_device_id, "ref_node_device_id")
            await self._create_record(
                label=RecordDataLabel.MULTILATERATION,
                data=RecordDataMultilateration(
                    ref_node_device_id=ref_node_device_id,
                    coordinates=coordinates,
                ),
                recorded_at=recorded_at,
                metadata=metadata,
                session=kwargs.get("session"),
            )
        except DomainException:
            raise
        except ValidationError as e:
            raise ValidatorDomainException(str(e)) from e
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to create multilateration record",
                {"error": str(e), "ref_node_device_id": ref_node_device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_multilateration_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Record]:
        tag = f"{self.tag_class}.read_multilateration_records_by_interval"
        try:
            query_filter = self._build_multilateration_filter(
                start=start,
                end=end,
                ref_node_device_ids=ref_node_device_ids,
                node_device_ids=node_device_ids,
            )
            return await self._read_records(query_filter, kwargs.get("session"))
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read multilateration records by interval",
                {
                    "error": str(e),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "ref_node_device_ids": ref_node_device_ids,
                    "node_device_ids": node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_latest_multilateration_record(
        self,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[Record]:
        tag = f"{self.tag_class}.read_latest_multilateration_record"
        try:
            query_filter = self._build_multilateration_filter(
                ref_node_device_ids=ref_node_device_ids,
                node_device_ids=node_device_ids,
            )
            return await self._read_latest_record(query_filter, kwargs.get("session"))
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read latest multilateration record",
                {
                    "error": str(e),
                    "ref_node_device_ids": ref_node_device_ids,
                    "node_device_ids": node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def delete_multilateration_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> int:
        tag = f"{self.tag_class}.delete_multilateration_records_by_interval"
        try:
            query_filter = self._build_multilateration_filter(
                start=start,
                end=end,
                ref_node_device_ids=ref_node_device_ids,
                node_device_ids=node_device_ids,
            )
            return await self._delete_records(query_filter, kwargs.get("session"))
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to delete multilateration records by interval",
                {
                    "error": str(e),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "ref_node_device_ids": ref_node_device_ids,
                    "node_device_ids": node_device_ids,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def _create_record(
        self,
        label: RecordDataLabel,
        data: RecordData,
        recorded_at: datetime,
        metadata: Optional[Dict[str, Any]],
        session: Any,
    ) -> None:
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

    async def _read_records(
        self,
        query_filter: Dict[str, Any],
        session: Any,
    ) -> List[Record]:
        docs = (
            await RecordDocument.find(query_filter, session=session)
            .sort("recorded_at")
            .to_list()
        )
        return [doc.to_domain() for doc in docs]

    async def _read_latest_record(
        self,
        query_filter: Dict[str, Any],
        session: Any,
    ) -> Optional[Record]:
        docs = (
            await RecordDocument.find(query_filter, session=session)
            .sort("-recorded_at")
            .limit(1)
            .to_list()
        )
        if not docs:
            return None
        return docs[0].to_domain()

    async def _delete_records(
        self,
        query_filter: Dict[str, Any],
        session: Any,
    ) -> int:
        result = await RecordDocument.get_motor_collection().delete_many(
            query_filter,
            session=session,
        )
        return result.deleted_count

    def _build_ranging_filter(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        source_node_device_ids: Optional[List[str]] = None,
        target_node_device_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        query_filter = self._build_label_filter(RecordDataLabel.RANGING, start, end)
        self._add_ids_filter(
            query_filter,
            RANGING_SOURCE_NODE_FIELD,
            source_node_device_ids,
            "source_node_device_ids",
        )
        self._add_ids_filter(
            query_filter,
            RANGING_TARGET_NODE_FIELD,
            target_node_device_ids,
            "target_node_device_ids",
        )
        return query_filter

    def _build_multilateration_filter(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        ref_node_device_ids: Optional[List[str]] = None,
        node_device_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        query_filter = self._build_label_filter(
            RecordDataLabel.MULTILATERATION,
            start,
            end,
        )
        self._add_ids_filter(
            query_filter,
            MULTILATERATION_REF_NODE_FIELD,
            ref_node_device_ids,
            "ref_node_device_ids",
        )
        self._add_ids_filter(
            query_filter,
            MULTILATERATION_NODE_FIELD,
            node_device_ids,
            "node_device_ids",
        )
        return query_filter

    def _build_label_filter(
        self,
        label: RecordDataLabel,
        start: Optional[datetime],
        end: Optional[datetime],
    ) -> Dict[str, Any]:
        query_filter: Dict[str, Any] = {"label": label}
        if start is not None and end is not None:
            validate_record_interval(start, end)
            query_filter["recorded_at"] = {
                "$gte": start,
                "$lte": end,
            }
        return query_filter

    def _add_ids_filter(
        self,
        query_filter: Dict[str, Any],
        field: str,
        ids: Optional[List[str]],
        label: str,
    ) -> None:
        if ids is None:
            return

        validate_ids_list(ids, label)
        query_filter[field] = {"$in": ids}
