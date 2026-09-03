from datetime import datetime, timezone

from beanie import Document, Link
from pydantic import Field
from pymongo import IndexModel

from ips_app.domain.models.position import PositionRecord
from ips_app.infrastructure.repository._shared.link import required_link
from ips_app.infrastructure.repository.node.beanie_model import NodeDocument
from ips_app.infrastructure.repository.node_network.beanie_model import (
    NodeNetworkDocument,
)


class PositionRecordDocument(Document):
    network: Link[NodeNetworkDocument]
    tag_node: Link[NodeDocument]
    x: float
    y: float
    tag_height: float = Field(..., ge=0)

    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "position_records"
        indexes = [
            IndexModel([("network.$id", 1), ("computed_at", 1)], name="position_network_computed_at"),
            IndexModel([("tag_node.$id", 1), ("computed_at", 1)], name="position_tag_node_computed_at"),
            [("computed_at", 1)],
        ]

    def to_domain(self) -> PositionRecord:
        network = required_link(self.network, field_name="network")
        tag_node = required_link(self.tag_node, field_name="tag_node")

        return PositionRecord(
            id=self.id,
            network=network.to_domain(),
            tag_node=tag_node.to_domain(),
            x=self.x,
            y=self.y,
            tag_height=self.tag_height,
            computed_at=self.computed_at,
        )
