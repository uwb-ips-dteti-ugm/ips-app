from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Annotated
from beanie import Document, Indexed, Link
from pydantic import Field
from ips_app.domain.models.permission import Permission

class Role(Document):
    name: Annotated[str, Indexed(unique=True)]
    description: str = Field(default="")
    preferences: Dict[str, Any] = Field(default_factory=dict)
    is_default: bool = Field(default=False)
    
    permissions: List[Link[Permission]] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = Field(default=0)

    class Settings:
        name = "roles"
        indexes = [
            [("is_default", 1)]
        ]
