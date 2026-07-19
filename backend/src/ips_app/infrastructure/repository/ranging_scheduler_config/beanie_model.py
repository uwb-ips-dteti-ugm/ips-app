from datetime import datetime, timezone
from typing import Any, Optional

from beanie import Document
from pydantic import Field

from ips_app.domain.models.ranging_scheduler_config import RangingSchedulerConfig


class RangingSchedulerConfigDocument(Document):
    listen_timeout_uus: int
    initiate_timeout_uus: int
    listen_to_initiate_delay_ms: int
    pair_delay_ms: int
    idle_delay_ms: int

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None

    class Settings:
        name = "ranging_scheduler_config"

    def to_domain(self) -> RangingSchedulerConfig:
        return RangingSchedulerConfig(
            id=self.id,
            listen_timeout_uus=self.listen_timeout_uus,
            initiate_timeout_uus=self.initiate_timeout_uus,
            listen_to_initiate_delay_ms=self.listen_to_initiate_delay_ms,
            pair_delay_ms=self.pair_delay_ms,
            idle_delay_ms=self.idle_delay_ms,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
        )
