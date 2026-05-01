from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Annotated
from beanie import Document, Indexed, Link
from pydantic import Field
from ips_app.domain.models.role import Role
from ips_app.domain.models.permission import Permission
from ips_app.adapters.driven.repository.permission.beanie_model import PermissionDocument


class RoleDocument(Document):
    name: Annotated[str, Indexed(unique=True)]
    description: str = Field(default="")
    preferences: Dict[str, Any] = Field(default_factory=dict)
    is_default: bool = Field(default=False)

    permissions: List[Link[PermissionDocument]] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = Field(default=0)

    class Settings:
        name = "roles"
        indexes = [
            [("is_default", 1)],
        ]

    def to_domain(self) -> Role:
        return Role(
            id=self.id,
            name=self.name,
            description=self.description,
            preferences=self.preferences,
            is_default=self.is_default,
            permissions=[
                link.to_domain() if isinstance(link, PermissionDocument) else Permission(id=link.ref.id, name="")
                for link in self.permissions
            ],
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
            version=self.version,
        )
