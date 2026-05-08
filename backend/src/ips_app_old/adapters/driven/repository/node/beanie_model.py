from datetime import datetime, timezone
from typing import Optional, Dict, Any, Annotated
from beanie import Document, Indexed
from pydantic import Field
from ips_app_old.domain.models.node import Node


class NodeDocument(Document):
    dev_id: Optional[Annotated[str, Indexed(unique=True)]] = None
    type: Optional[Annotated[str, Indexed()]] = None
    name: Optional[Annotated[str, Indexed()]] = Field(default="Unknown Node")
    description: str = Field(default="")
    preferences: Dict[str, Any] = Field(default_factory=dict)
    connected: bool = Field(default=False)

    approved_at: Optional[datetime] = None
    approved_by: Optional[Any] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = Field(default=0)

    class Settings:
        name = "nodes"
        indexes = [
            [("connected", 1)],
            [("approved_at", 1)],
        ]

    def to_domain(self) -> Node:
        return Node(
            id=self.id,
            dev_id=self.dev_id or "",
            type=self.type or "",
            name=self.name or "Unknown Node",
            description=self.description,
            preferences=self.preferences,
            connected=self.connected,
            approved_at=self.approved_at,
            approved_by=self.approved_by,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
            version=self.version,
        )
