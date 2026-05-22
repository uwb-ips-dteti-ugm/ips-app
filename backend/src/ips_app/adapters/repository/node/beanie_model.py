from datetime import datetime, timezone
from typing import Annotated, Any, Dict, Optional

from beanie import Document, Indexed, Link
from pydantic import Field
from pymongo import IndexModel

from ips_app.adapters.repository.node_network.beanie_model import (
    NodeNetworkDocument,
)
from ips_app.domain.models.node import Node, NodeStatus
from ips_app.domain.models.node_network import NodeNetwork


class NodeDocument(Document):
    device_id: Annotated[str, Indexed(unique=True)]
    name: Annotated[str, Indexed()]
    description: str = Field(default="")
    network: Optional[Link[NodeNetworkDocument]] = None
    address: Optional[int] = Field(None, ge=0, le=0xFFFF)
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

    class Settings:
        name = "nodes"
        indexes = [
            [("status", 1)],
            [("network.$id", 1)],
            [("address", 1)],
            IndexModel(
                [("network.$id", 1), ("address", 1)],
                unique=True,
                name="unique_node_network_address",
                partialFilterExpression={
                    "network.$id": {"$exists": True},
                    "address": {"$exists": True},
                },
            ),
        ]

    def to_domain(self) -> Node:
        network: Optional[NodeNetwork] = None
        if isinstance(self.network, NodeNetworkDocument):
            network = self.network.to_domain()
        elif network_ref := getattr(self.network, "ref", None):
            network = NodeNetwork(id=network_ref.id, pan_id=0, name="")
        elif network_value := getattr(self.network, "value", None):
            network = network_value.to_domain()

        return Node(
            id=self.id,
            device_id=self.device_id,
            name=self.name,
            description=self.description,
            network=network,
            address=self.address,
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
        )
