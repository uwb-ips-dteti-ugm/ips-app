from datetime import datetime, timezone
from enum import StrEnum, IntEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


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
    version: int = 0

    @property
    def can_record(self) -> bool:
        return self.status == NodeStatus.APPROVED
