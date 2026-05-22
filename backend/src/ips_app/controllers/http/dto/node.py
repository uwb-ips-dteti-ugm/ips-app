from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.controllers.http.dto.common import PaginationMeta
from ips_app.controllers.http.dto.node_network import NodeNetworkResponse
from ips_app.domain.models.exception import ValidatorDomainException
from ips_app.domain.models.node import Node, NodeStatus
from ips_app.utils.validator import (
    validate_description,
    validate_name,
    validate_non_empty_string,
    validate_preferences,
)


class AddNodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: str = Field(..., examples=["node-anchor-001"])
    name: str = Field(..., examples=["Anchor North"])
    description: str = Field("", examples=["North wall anchor node"])
    network_id: Optional[str] = Field(None, examples=["507f1f77bcf86cd799439011"])
    address: Optional[int] = Field(None, ge=0, le=0xFFFF, examples=[1])
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        examples=[{"x": 0, "y": 0, "z": 0}],
    )

    def validate_fields(self) -> None:
        validate_non_empty_string(self.device_id, "device_id")
        validate_name(self.name)
        validate_description(self.description)
        validate_preferences(self.preferences)
        if (self.network_id is None) != (self.address is None):
            raise ValidatorDomainException(
                "'network_id' and 'address' must be provided together."
            )
        if self.network_id is not None:
            validate_non_empty_string(self.network_id, "network_id")


class SetNodeInfoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(None, examples=["Anchor North East"])
    description: Optional[str] = Field(None, examples=["Updated anchor placement"])

    def validate_fields(self) -> None:
        if self.name is not None:
            validate_name(self.name)
        if self.description is not None:
            validate_description(self.description)


class SetNodeNetworkAssignmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    network_id: Optional[str] = Field(None, examples=["507f1f77bcf86cd799439011"])
    address: Optional[int] = Field(None, ge=0, le=0xFFFF, examples=[1])

    def validate_fields(self) -> None:
        if (self.network_id is None) != (self.address is None):
            raise ValidatorDomainException(
                "'network_id' and 'address' must be provided together."
            )
        if self.network_id is not None:
            validate_non_empty_string(self.network_id, "network_id")


class SetNodeStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: NodeStatus = Field(..., examples=[NodeStatus.APPROVED])


class AddRangingRecordByAddressesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reported_by_device_id: str = Field(..., examples=["node-anchor-001"])
    pan_id: int = Field(..., ge=0, le=0xFFFF, examples=[4660])
    source_address: int = Field(..., ge=0, le=0xFFFF, examples=[1])
    destination_address: int = Field(..., ge=0, le=0xFFFF, examples=[2])
    distance: float = Field(..., ge=0, examples=[2.42])

    def validate_fields(self) -> None:
        validate_non_empty_string(self.reported_by_device_id, "reported_by_device_id")


class NodeRegistrationResponse(BaseModel):
    device_id: str = Field(..., examples=["node-anchor-001"])
    is_registered: bool = Field(..., examples=[True])


class RegisteredNodesResponse(BaseModel):
    data: List[str] = Field(..., examples=[["node-anchor-001", "node-tag-001"]])


class NodeResponse(BaseModel):
    id: str = Field(..., examples=["507f1f77bcf86cd799439011"])
    device_id: str = Field(..., examples=["node-anchor-001"])
    name: str = Field(..., examples=["Anchor North"])
    description: str = Field(..., examples=["North wall anchor node"])
    network: Optional[NodeNetworkResponse] = None
    address: Optional[int] = Field(None, examples=[1])
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        examples=[{"x": 0, "y": 0, "z": 0}],
    )
    status: NodeStatus = Field(..., examples=[NodeStatus.APPROVED])
    is_approved: bool = Field(..., examples=[True])
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = Field(None, examples=["507f1f77bcf86cd799439011"])
    last_seen_at: Optional[datetime] = None
    last_connected_at: Optional[datetime] = None
    last_disconnected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_domain(cls, node: Node) -> NodeResponse:
        return cls(
            id=str(node.id),
            device_id=node.device_id,
            name=node.name,
            description=node.description,
            network=(
                NodeNetworkResponse.from_domain(node.network)
                if node.network is not None
                else None
            ),
            address=node.address,
            preferences=node.preferences,
            status=node.status,
            is_approved=node.is_approved,
            approved_at=node.approved_at,
            approved_by=str(node.approved_by) if node.approved_by is not None else None,
            last_seen_at=node.last_seen_at,
            last_connected_at=node.last_connected_at,
            last_disconnected_at=node.last_disconnected_at,
            created_at=node.created_at,
            updated_at=node.updated_at,
        )


class NodesResponse(BaseModel):
    data: List[NodeResponse]
    meta: PaginationMeta

    @classmethod
    def from_domain(
        cls,
        items: List[Node],
        page: int,
        limit: int,
        total: int,
    ) -> NodesResponse:
        return cls(
            data=[NodeResponse.from_domain(node) for node in items],
            meta=PaginationMeta(page=page, limit=limit, total=total),
        )
