from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from ips_app.domain.models.permission import Permission


class Role(BaseModel):
    id: Optional[Any] = None
    name: str
    description: str = ""
    preferences: Dict[str, Any] = Field(default_factory=dict)
    is_default: bool = False

    permissions: List[Permission] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None
