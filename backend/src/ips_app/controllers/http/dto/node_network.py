from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.controllers.http.dto.common import PaginationMeta
from ips_app.domain.models.node_network import NodeNetwork
from ips_app.utils.validator import validate_description, validate_name


class AddNodeNetworkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pan_id: int = Field(..., ge=0, le=0xFFFF, examples=[4660])
    name: str = Field(..., examples=["Main UWB Network"])
    description: str = Field("", examples=["Primary network for anchor nodes"])

    def validate_fields(self) -> None:
        validate_name(self.name)
        validate_description(self.description)


class SetNodeNetworkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pan_id: Optional[int] = Field(None, ge=0, le=0xFFFF, examples=[4661])
    name: Optional[str] = Field(None, examples=["Updated UWB Network"])
    description: Optional[str] = Field(None, examples=["Updated network description"])

    def validate_fields(self) -> None:
        if self.name is not None:
            validate_name(self.name)
        if self.description is not None:
            validate_description(self.description)


class NodeNetworkResponse(BaseModel):
    id: str = Field(..., examples=["507f1f77bcf86cd799439011"])
    pan_id: int = Field(..., examples=[4660])
    name: str = Field(..., examples=["Main UWB Network"])
    description: str = Field(..., examples=["Primary network for anchor nodes"])
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_domain(cls, node_network: NodeNetwork) -> NodeNetworkResponse:
        return cls(
            id=str(node_network.id),
            pan_id=node_network.pan_id,
            name=node_network.name,
            description=node_network.description,
            created_at=node_network.created_at,
            updated_at=node_network.updated_at,
        )


class NodeNetworksResponse(BaseModel):
    data: List[NodeNetworkResponse]
    meta: PaginationMeta

    @classmethod
    def from_domain(
        cls,
        items: List[NodeNetwork],
        page: int,
        limit: int,
        total: int,
    ) -> NodeNetworksResponse:
        return cls(
            data=[
                NodeNetworkResponse.from_domain(node_network)
                for node_network in items
            ],
            meta=PaginationMeta(page=page, limit=limit, total=total),
        )
