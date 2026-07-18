from datetime import datetime, timezone
from enum import StrEnum, IntEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class NodeCommandCode(IntEnum):
    RESTART = 1
    RANGING_LISTEN = 2
    RANGING_INITIATE = 3


class NodeStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    SUSPENDED = "suspended"


class NodeNetwork(BaseModel):
    id: Optional[Any] = None
    pan_id: int = Field(..., ge=0, le=0xFFFF)
    name: str = Field(..., min_length=1)
    description: str = Field("", max_length=2000)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None


class Node(BaseModel):
    id: Optional[Any] = None
    device_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = Field("", max_length=2000)
    address: Optional[int] = Field(None, ge=0, le=0xFFFF)
    status: NodeStatus = NodeStatus.PENDING
    approved_at: Optional[datetime] = None
    approved_by: Optional[Any] = None
    last_seen_at: Optional[datetime] = None
    last_connected_at: Optional[datetime] = None
    last_disconnected_at: Optional[datetime] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)

    network: Optional[NodeNetwork] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None
