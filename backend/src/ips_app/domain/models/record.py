from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator


class RecordDataLabel(StrEnum):
    RANGING = "ranging"
    MULTILATERATION = "multilateration"


class RecordDataRanging(BaseModel):
    source_node_device_id: str
    target_node_device_id: str
    distance: float = Field(..., ge=0)


class RecordDataMultilateration(BaseModel):
    class MultilaterationCoordinate(BaseModel):
        node_device_id: str
        x: float
        y: float
        z: float

    ref_node_device_id: str
    coordinates: List[MultilaterationCoordinate] = Field(default_factory=list)


RecordData = Union[RecordDataRanging, RecordDataMultilateration]


class Record(BaseModel):
    id: Optional[Any] = None
    label: RecordDataLabel
    data: RecordData
    metadata: Dict[str, Any] = Field(default_factory=dict)

    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="before")
    @classmethod
    def parse_data_from_label(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        label = value.get("label")
        data = value.get("data")
        if data is None or isinstance(data, BaseModel):
            return value

        if label == RecordDataLabel.RANGING or label == RecordDataLabel.RANGING.value:
            value["data"] = RecordDataRanging.model_validate(data)
        elif (
            label == RecordDataLabel.MULTILATERATION
            or label == RecordDataLabel.MULTILATERATION.value
        ):
            value["data"] = RecordDataMultilateration.model_validate(data)

        return value

    @model_validator(mode="after")
    def validate_data_matches_label(self) -> "Record":
        if self.label == RecordDataLabel.RANGING and not isinstance(
            self.data,
            RecordDataRanging,
        ):
            raise ValueError("'ranging' records must use ranging data.")

        if self.label == RecordDataLabel.MULTILATERATION and not isinstance(
            self.data,
            RecordDataMultilateration,
        ):
            raise ValueError(
                "'multilateration' records must use multilateration data."
            )

        return self
