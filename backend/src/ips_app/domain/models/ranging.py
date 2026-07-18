from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field
from ips_app.domain.models.node import Node, NodeNetwork


class RangingPair(BaseModel):
    network: NodeNetwork
    listener_node: Node
    initiator_node: Node
    cycle_done: bool


class RangingRecord(BaseModel):
    id: Optional[Any] = None
    network: NodeNetwork
    listener_node: Node
    initiator_node: Node
    distance: float = Field(..., ge=0)

    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
