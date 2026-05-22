from datetime import datetime, timezone
from typing import Any, Dict

from beanie import Document
from pydantic import Field
from pymongo import IndexModel

from ips_app.domain.models.record import Record, RecordData, RecordDataLabel


class RecordDocument(Document):
    label: RecordDataLabel
    data: RecordData
    metadata: Dict[str, Any] = Field(default_factory=dict)

    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "records"
        indexes = [
            [("label", 1)],
            IndexModel(
                [("label", 1), ("recorded_at", 1)],
                name="record_label_recorded_at",
            ),
            IndexModel(
                [("label", 1), ("data.source_node_device_id", 1), ("recorded_at", 1)],
                name="record_label_ranging_source_recorded_at",
            ),
            IndexModel(
                [("label", 1), ("data.target_node_device_id", 1), ("recorded_at", 1)],
                name="record_label_ranging_target_recorded_at",
            ),
            IndexModel(
                [("label", 1), ("data.ref_node_device_id", 1), ("recorded_at", 1)],
                name="record_label_multilateration_ref_recorded_at",
            ),
            IndexModel(
                [
                    ("label", 1),
                    ("data.coordinates.node_device_id", 1),
                    ("recorded_at", 1),
                ],
                name="record_label_multilateration_node_recorded_at",
            ),
        ]

    def to_domain(self) -> Record:
        return Record(
            id=self.id,
            label=self.label,
            data=self.data,
            metadata=self.metadata,
            recorded_at=self.recorded_at,
        )
