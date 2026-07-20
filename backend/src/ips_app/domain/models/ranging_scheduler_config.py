from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class RangingSchedulerConfig(BaseModel):
    id: Optional[Any] = None
    listen_timeout_uus: int = Field(..., gt=0)
    initiate_timeout_uus: int = Field(..., gt=0)
    listen_to_initiate_delay_ms: int = Field(..., gt=0)
    pair_delay_ms: int = Field(..., gt=0)
    idle_delay_ms: int = Field(..., gt=0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None
