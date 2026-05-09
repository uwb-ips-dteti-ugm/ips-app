from datetime import datetime, timezone
from typing import Annotated, Any, Dict, Optional

from beanie import Document, Indexed
from pydantic import Field

from ips_app.domain.models.node import Node, NodeStatus


class NodeDocument(Document):
    device_id: Annotated[str, Indexed(unique=True)]
    name: Annotated[str, Indexed()]
    description: str = Field(default="")
    preferences: Dict[str, Any] = Field(default_factory=dict)

    status: NodeStatus = Field(default=NodeStatus.PENDING)
    approved_at: Optional[datetime] = None
    approved_by: Optional[Any] = None

    last_seen_at: Optional[datetime] = None
    last_connected_at: Optional[datetime] = None
    last_disconnected_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None
    version: int = Field(default=0)

    class Settings:
        name = "nodes"
        indexes = [
            [("status", 1)],
            [("last_seen_at", -1)],
            [("last_connected_at", -1)],
        ]

    def to_domain(self) -> Node:
        return Node(
            id=self.id,
            device_id=self.device_id,
            name=self.name,
            description=self.description,
            preferences=self.preferences,
            status=self.status,
            approved_at=self.approved_at,
            approved_by=self.approved_by,
            last_seen_at=self.last_seen_at,
            last_connected_at=self.last_connected_at,
            last_disconnected_at=self.last_disconnected_at,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
            version=self.version,
        )
