from datetime import datetime, timezone

from beanie import Document, Link
from pydantic import Field
from pymongo import IndexModel

from ips_app.domain.models.ranging import RangingRecord
from ips_app.infrastructure.repository._shared.link import required_link
from ips_app.infrastructure.repository.node.beanie_model import NodeDocument
from ips_app.infrastructure.repository.node_network.beanie_model import (
    NodeNetworkDocument,
)


class RangingRecordDocument(Document):
    network: Link[NodeNetworkDocument]
    listener_node: Link[NodeDocument]
    initiator_node: Link[NodeDocument]
    distance: float = Field(..., ge=0)

    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "ranging_records"
        indexes = [
            IndexModel([("network.$id", 1), ("recorded_at", 1)], name="ranging_network_recorded_at"),
            IndexModel([("listener_node.$id", 1), ("recorded_at", 1)], name="ranging_listener_recorded_at"),
            IndexModel([("initiator_node.$id", 1), ("recorded_at", 1)], name="ranging_initiator_recorded_at"),
            [("recorded_at", 1)],
        ]

    def to_domain(self) -> RangingRecord:
        network = required_link(self.network, field_name="network")
        listener_node = required_link(self.listener_node, field_name="listener_node")
        initiator_node = required_link(self.initiator_node, field_name="initiator_node")

        return RangingRecord(
            id=self.id,
            network=network.to_domain(),
            listener_node=listener_node.to_domain(),
            initiator_node=initiator_node.to_domain(),
            distance=self.distance,
            recorded_at=self.recorded_at,
        )
