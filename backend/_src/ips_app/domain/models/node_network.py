from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class NodeNetwork(BaseModel):
    id: Optional[Any] = None
    pan_id: int = Field(..., ge=0, le=0xFFFF)
    name: str
    description: str = ""

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None
