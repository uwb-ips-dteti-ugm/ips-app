from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.domain.models.node_network import NodeNetwork
from ips_app.presentation.http.dto.common import AuditedResponse, stringify_id


class CreateNodeNetworkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pan_id: int = Field(..., ge=0, le=0xFFFF, examples=[1])
    name: str = Field(..., examples=["lab-network"])
    description: str = Field("", examples=["Lab UWB network"])


class UpdateNodeNetworkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pan_id: Optional[int] = Field(None, ge=0, le=0xFFFF)
    name: Optional[str] = None
    description: Optional[str] = None


class NodeNetworkResponse(AuditedResponse):
    id: str
    pan_id: int
    name: str
    description: str

    @classmethod
    def from_domain(cls, node_network: NodeNetwork) -> "NodeNetworkResponse":
        return cls(
            id=str(node_network.id),
            pan_id=node_network.pan_id,
            name=node_network.name,
            description=node_network.description,
            created_at=node_network.created_at,
            created_by=stringify_id(node_network.created_by),
            updated_at=node_network.updated_at,
            updated_by=stringify_id(node_network.updated_by),
        )
