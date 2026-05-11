from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.controllers.http.dto.common import PaginationMeta
from ips_app.domain.models.node import Node, NodeStatus
from ips_app.utils.validator import (
    validate_description,
    validate_name,
    validate_non_empty_string,
    validate_optional_non_negative_float,
)


class AddNodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: str = Field(..., examples=["node-anchor-001"])
    name: str = Field(..., examples=["Anchor North"])
    description: str = Field("", examples=["North wall anchor node"])

    def validate_fields(self) -> None:
        validate_non_empty_string(self.device_id, "device_id")
        validate_name(self.name)
        validate_description(self.description)


class SetNodeInfoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(None, examples=["Anchor North East"])
    description: Optional[str] = Field(None, examples=["Updated anchor placement"])

    def validate_fields(self) -> None:
        if self.name is not None:
            validate_name(self.name)
        if self.description is not None:
            validate_description(self.description)


class SetNodeStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: NodeStatus = Field(..., examples=[NodeStatus.APPROVED])


class AddRangingRecordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_node_device_id: Optional[str] = Field(None, examples=["node-anchor-001"])
    target_node_device_id: Optional[str] = Field(None, examples=["node-tag-001"])
    distance: Optional[float] = Field(None, examples=[2.42])
    recorded_at: datetime
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        examples=[{"sequence": 1, "unit": "meter"}],
    )

    def validate_fields(self) -> None:
        if self.source_node_device_id is not None:
            validate_non_empty_string(
                self.source_node_device_id,
                "source_node_device_id",
            )
        if self.target_node_device_id is not None:
            validate_non_empty_string(
                self.target_node_device_id,
                "target_node_device_id",
            )
        validate_optional_non_negative_float(self.distance, "distance")


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
    created_by: Optional[str] = Field(None, examples=["507f1f77bcf86cd799439011"])
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = Field(None, examples=["507f1f77bcf86cd799439011"])
    version: int = Field(..., examples=[1])

    @classmethod
    def from_domain(cls, node: Node) -> NodeResponse:
        return cls(
            id=str(node.id),
            device_id=node.device_id,
            name=node.name,
            description=node.description,
            preferences=node.preferences,
            status=node.status,
            is_approved=node.is_approved,
            approved_at=node.approved_at,
            approved_by=str(node.approved_by) if node.approved_by is not None else None,
            last_seen_at=node.last_seen_at,
            last_connected_at=node.last_connected_at,
            last_disconnected_at=node.last_disconnected_at,
            created_at=node.created_at,
            created_by=str(node.created_by) if node.created_by is not None else None,
            updated_at=node.updated_at,
            updated_by=str(node.updated_by) if node.updated_by is not None else None,
            version=node.version,
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
