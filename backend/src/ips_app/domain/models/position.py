from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from ips_app.domain.models.node import Node
from ips_app.domain.models.node_network import NodeNetwork


class PositionRecord(BaseModel):
    id: Optional[Any] = None
    network: NodeNetwork
    tag_node: Node
    x: float
    y: float
    tag_height: float = Field(..., ge=0)

    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
