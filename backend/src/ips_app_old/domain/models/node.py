from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Node(BaseModel):
    id: Optional[Any] = None
    dev_id: str
    type: str
    name: str = "Unknown Node"
    connected: bool = False
    description: str = ""
    preferences: Dict[str, Any] = Field(default_factory=dict)

    approved_at: Optional[datetime] = None
    approved_by: Optional[Any] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = 0
