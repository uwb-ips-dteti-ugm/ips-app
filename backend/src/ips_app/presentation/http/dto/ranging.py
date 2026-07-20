from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ips_app.domain.models.ranging import RangingRecord
from ips_app.presentation.http.dto.node import NodeResponse
from ips_app.presentation.http.dto.node_network import NodeNetworkResponse


class ReportRangingMeasurementRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reported_by_device_id: str = Field(..., examples=["node-001"])
    pan_id: int = Field(..., ge=0, le=0xFFFF)
    source_address: int = Field(..., ge=0, le=0xFFFF)
    destination_address: int = Field(..., ge=0, le=0xFFFF)
    distance: float = Field(..., ge=0)


class RangingRecordResponse(BaseModel):
    id: str
    network: NodeNetworkResponse
    listener_node: NodeResponse
    initiator_node: NodeResponse
    distance: float
    recorded_at: datetime

    @classmethod
    def from_domain(cls, record: RangingRecord) -> "RangingRecordResponse":
        return cls(
            id=str(record.id),
            network=NodeNetworkResponse.from_domain(record.network),
            listener_node=NodeResponse.from_domain(record.listener_node),
            initiator_node=NodeResponse.from_domain(record.initiator_node),
            distance=record.distance,
            recorded_at=record.recorded_at,
        )


class DeleteRangingRecordsResponse(BaseModel):
    deleted_count: int
