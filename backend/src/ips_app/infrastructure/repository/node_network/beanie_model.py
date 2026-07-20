from datetime import datetime, timezone
from typing import Annotated, Any, Optional

from beanie import Document, Indexed
from pydantic import Field

from ips_app.domain.models.node_network import NodeNetwork


class NodeNetworkDocument(Document):
    pan_id: Annotated[int, Indexed(unique=True)] = Field(..., ge=0, le=0xFFFF)
    name: Annotated[str, Indexed()]
    description: str = Field(default="")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None

    class Settings:
        name = "node_networks"

    def to_domain(self) -> NodeNetwork:
        return NodeNetwork(
            id=self.id,
            pan_id=self.pan_id,
            name=self.name,
            description=self.description,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
        )
