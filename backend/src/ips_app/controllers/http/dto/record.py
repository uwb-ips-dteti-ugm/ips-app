from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from ips_app.domain.models.record import (
    Record,
    RecordData,
    RecordDataLabel,
    RecordDataMultilateration,
    RecordDataRanging,
)
from ips_app.domain.ports.driven.repository.record import RecordIntervalField
from ips_app.utils.validator import validate_ids_list, validate_record_interval


class RecordIntervalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: RecordDataLabel = Field(..., examples=[RecordDataLabel.RANGING])
    interval_field: RecordIntervalField = Field("recorded_at", examples=["recorded_at"])
    start: datetime
    end: datetime
    source_node_device_ids: Optional[List[str]] = Field(
        None,
        examples=[["node-anchor-001"]],
    )
    target_node_device_ids: Optional[List[str]] = Field(
        None,
        examples=[["node-tag-001"]],
    )

    def validate_fields(self) -> None:
        validate_record_interval(self.interval_field, self.start, self.end)
        if self.source_node_device_ids is not None:
            validate_ids_list(self.source_node_device_ids, "source_node_device_ids")
        if self.target_node_device_ids is not None:
            validate_ids_list(self.target_node_device_ids, "target_node_device_ids")


class RemoveRecordsByIntervalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: RecordDataLabel = Field(..., examples=[RecordDataLabel.RANGING])
    interval_field: RecordIntervalField = Field("recorded_at", examples=["recorded_at"])
    start: datetime
    end: datetime
    source_node_device_ids: Optional[List[str]] = Field(
        None,
        examples=[["node-anchor-001"]],
    )

    def validate_fields(self) -> None:
        validate_record_interval(self.interval_field, self.start, self.end)
        if self.source_node_device_ids is not None:
            validate_ids_list(self.source_node_device_ids, "source_node_device_ids")


class RecordDataRangingResponse(BaseModel):
    source_node_device_id: Optional[str] = Field(None, examples=["node-anchor-001"])
    target_node_device_id: Optional[str] = Field(None, examples=["node-tag-001"])
    distance: Optional[float] = Field(None, examples=[2.42])

    @classmethod
    def from_domain(
        cls,
        data: RecordDataRanging,
    ) -> RecordDataRangingResponse:
        return cls(
            source_node_device_id=data.source_node_device_id,
            target_node_device_id=data.target_node_device_id,
            distance=data.distance,
        )


class MultilaterationCoordinateResponse(BaseModel):
    node_device_id: str = Field(..., examples=["node-tag-001"])
    x: float = Field(..., examples=[1.2])
    y: float = Field(..., examples=[3.4])
    z: float = Field(..., examples=[0.0])

    @classmethod
    def from_domain(
        cls,
        coordinate: RecordDataMultilateration.MultilaterationCoordinate,
    ) -> MultilaterationCoordinateResponse:
        return cls(
            node_device_id=coordinate.node_device_id,
            x=coordinate.x,
            y=coordinate.y,
            z=coordinate.z,
        )


class RecordDataMultilaterationResponse(BaseModel):
    ref_node_device_id: str = Field(..., examples=["node-anchor-001"])
    coordinates: List[MultilaterationCoordinateResponse] = Field(default_factory=list)

    @classmethod
    def from_domain(
        cls,
        data: RecordDataMultilateration,
    ) -> RecordDataMultilaterationResponse:
        return cls(
            ref_node_device_id=data.ref_node_device_id,
            coordinates=[
                MultilaterationCoordinateResponse.from_domain(coordinate)
                for coordinate in data.coordinates
            ],
        )


RecordDataResponse = Union[
    RecordDataRangingResponse,
    RecordDataMultilaterationResponse,
]


class RecordResponse(BaseModel):
    id: Optional[str] = Field(None, examples=["507f1f77bcf86cd799439011"])
    label: RecordDataLabel = Field(..., examples=[RecordDataLabel.RANGING])
    data: RecordDataResponse
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        examples=[{"sequence": 1, "unit": "meter"}],
    )
    recorded_at: datetime
    created_at: datetime

    @classmethod
    def from_domain(cls, record: Record) -> RecordResponse:
        return cls(
            id=str(record.id) if record.id is not None else None,
            label=record.label,
            data=map_record_data_response(record.data),
            metadata=record.metadata,
            recorded_at=record.recorded_at,
            created_at=record.created_at,
        )


class RecordsResponse(BaseModel):
    data: List[RecordResponse]

    @classmethod
    def from_domain(cls, records: List[Record]) -> RecordsResponse:
        return cls(
            data=[RecordResponse.from_domain(record) for record in records],
        )


class RemovedRecordsResponse(BaseModel):
    deleted_count: int = Field(..., examples=[42])


def map_record_data_response(data: RecordData) -> RecordDataResponse:
    if isinstance(data, RecordDataRanging):
        return RecordDataRangingResponse.from_domain(data)
    return RecordDataMultilaterationResponse.from_domain(data)
