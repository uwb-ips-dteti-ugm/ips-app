from datetime import datetime, timezone
from enum import StrEnum, IntEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator

from ips_app.domain.models.node_network import NodeNetwork


class NodeCommandCode(IntEnum):
    RESTART = 1
    LISTEN_RANGING = 2
    INITIATE_RANGING = 3


class NodeStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class Node(BaseModel):
    id: Optional[Any] = None
    device_id: str
    name: str
    description: str = ""
    network: Optional[NodeNetwork] = None
    address: Optional[int] = Field(None, ge=0, le=0xFFFF)
    preferences: Dict[str, Any] = Field(default_factory=dict)

    status: NodeStatus = NodeStatus.PENDING
    approved_at: Optional[datetime] = None
    approved_by: Optional[Any] = None

    last_seen_at: Optional[datetime] = None
    last_connected_at: Optional[datetime] = None
    last_disconnected_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None

    @property
    def is_approved(self) -> bool:
        return self.status == NodeStatus.APPROVED

    @model_validator(mode="after")
    def validate_network_assignment(self) -> "Node":
        has_network = self.network is not None
        has_address = self.address is not None

        if has_network != has_address:
            raise ValueError(
                "'network' and 'address' must be provided together."
            )

        if self.status == NodeStatus.APPROVED and not has_network:
            raise ValueError(
                "Approved nodes must have a network and address."
            )

        return self
