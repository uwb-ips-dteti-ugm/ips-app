from datetime import datetime, timezone
from typing import Optional, Dict, Any, Annotated
from beanie import Document, Indexed
from pydantic import Field
from ips_app_old.domain.models.permission import Permission


class PermissionDocument(Document):
    name: Optional[Annotated[str, Indexed(unique=True)]] = None
    description: str = Field(default="")
    preferences: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = Field(default=0)

    class Settings:
        name = "permissions"

    def to_domain(self) -> Permission:
        return Permission(
            id=self.id,
            name=self.name or "",
            description=self.description,
            preferences=self.preferences,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
            version=self.version,
        )
