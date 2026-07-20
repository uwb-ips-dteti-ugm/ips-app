from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.domain.models.node import Node, NodeStatus
from ips_app.presentation.http.dto.common import AuditedResponse, stringify_id
from ips_app.presentation.http.dto.node_network import NodeNetworkResponse


class CreateNodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    device_id: str = Field(..., examples=["node-001"])
    name: str = Field(..., examples=["Hallway sensor"])
    description: str = Field("", examples=["Ceiling-mounted UWB sensor"])
    network_id: Optional[str] = None
    address: Optional[int] = Field(None, ge=0, le=0xFFFF)
    preferences: Optional[Dict[str, Any]] = None


class UpdateNodeInfoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    description: Optional[str] = None


class UpdateNodeNetworkAssignmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    network_id: Optional[str] = None
    address: Optional[int] = Field(None, ge=0, le=0xFFFF)


class UpdateNodeStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: NodeStatus


class UpdateNodePreferencesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    preferences: Dict[str, Any]


class NodeResponse(AuditedResponse):
    id: str
    device_id: str
    name: str
    description: str
    address: Optional[int]
    board_variant: Optional[str]
    status: NodeStatus
    approved_at: Optional[datetime]
    approved_by: Optional[str]
    last_seen_at: Optional[datetime]
    last_connected_at: Optional[datetime]
    last_disconnected_at: Optional[datetime]
    preferences: Dict[str, Any]
    network: Optional[NodeNetworkResponse]

    @classmethod
    def from_domain(cls, node: Node) -> "NodeResponse":
        return cls(
            id=str(node.id),
            device_id=node.device_id,
            name=node.name,
            description=node.description,
            address=node.address,
            board_variant=node.board_variant,
            status=node.status,
            approved_at=node.approved_at,
            approved_by=stringify_id(node.approved_by),
            last_seen_at=node.last_seen_at,
            last_connected_at=node.last_connected_at,
            last_disconnected_at=node.last_disconnected_at,
            preferences=node.preferences,
            network=NodeNetworkResponse.from_domain(node.network) if node.network else None,
            created_at=node.created_at,
            created_by=stringify_id(node.created_by),
            updated_at=node.updated_at,
            updated_by=stringify_id(node.updated_by),
        )


class RegisteredNodesResponse(BaseModel):
    device_ids: List[str]


class NodeRegistrationResponse(BaseModel):
    device_id: str
    is_connected: bool
