from datetime import datetime, timezone
from typing import Optional, Dict, Any, Annotated
from beanie import Document, Indexed
from pydantic import Field

class Permission(Document):
    name: Annotated[str, Indexed(unique=True)]
    description: str = Field(default="")
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = Field(default=0)

    class Settings:
        name = "permissions"
