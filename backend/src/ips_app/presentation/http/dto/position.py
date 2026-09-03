from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ips_app.domain.models.position import PositionRecord
from ips_app.presentation.http.dto.node import NodeResponse
from ips_app.presentation.http.dto.node_network import NodeNetworkResponse


class ComputeTagPositionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tag_node_id: str = Field(..., examples=["node-001"])
    tag_height: float = Field(1.0, ge=0)


class PositionRecordResponse(BaseModel):
    id: str
    network: NodeNetworkResponse
    tag_node: NodeResponse
    x: float
    y: float
    tag_height: float
    computed_at: datetime

    @classmethod
    def from_domain(cls, record: PositionRecord) -> "PositionRecordResponse":
        return cls(
            id=str(record.id),
            network=NodeNetworkResponse.from_domain(record.network),
            tag_node=NodeResponse.from_domain(record.tag_node),
            x=record.x,
            y=record.y,
            tag_height=record.tag_height,
            computed_at=record.computed_at,
        )
