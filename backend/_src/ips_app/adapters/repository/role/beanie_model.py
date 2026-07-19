from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, Optional

from beanie import Document, Indexed, Link
from pydantic import Field

from ips_app.adapters.repository.permission.beanie_model import PermissionDocument
from ips_app.domain.models.permission import Permission
from ips_app.domain.models.role import Role


class RoleDocument(Document):
    name: Annotated[str, Indexed(unique=True)]
    description: str = Field(default="")
    preferences: Dict[str, Any] = Field(default_factory=dict)
    is_default: bool = Field(default=False)
    permissions: List[Link[PermissionDocument]] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None

    class Settings:
        name = "roles"
        indexes = [
            [("is_default", 1)],
        ]

    def to_domain(self) -> Role:
        permissions: List[Permission] = []
        for permission in self.permissions:
            if isinstance(permission, PermissionDocument):
                permissions.append(permission.to_domain())
            elif permission_ref := getattr(permission, "ref", None):
                permissions.append(Permission(id=permission_ref.id, name=""))
            elif permission_value := getattr(permission, "value", None):
                permissions.append(permission_value.to_domain())

        return Role(
            id=self.id,
            name=self.name,
            description=self.description,
            preferences=self.preferences,
            is_default=self.is_default,
            permissions=permissions,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
        )
