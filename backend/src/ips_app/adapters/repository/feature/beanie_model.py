from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, Optional

from beanie import Document, Indexed, Link
from pydantic import Field

from ips_app.adapters.repository.permission.beanie_model import PermissionDocument
from ips_app.domain.models.feature import Feature
from ips_app.domain.models.permission import Permission


class FeatureDocument(Document):
    name: Annotated[str, Indexed(unique=True)]
    description: str = Field(default="")
    preferences: Dict[str, Any] = Field(default_factory=dict)
    permissions: List[Link[PermissionDocument]] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = Field(default=0)

    class Settings:
        name = "features"

    def to_domain(self) -> Feature:
        permissions: List[Permission] = []
        for permission in self.permissions:
            if isinstance(permission, PermissionDocument):
                permissions.append(permission.to_domain())
            elif permission_ref := getattr(permission, "ref", None):
                permissions.append(Permission(id=permission_ref.id, name=""))
            elif permission_value := getattr(permission, "value", None):
                permissions.append(permission_value.to_domain())

        return Feature(
            id=self.id,
            name=self.name,
            description=self.description,
            preferences=self.preferences,
            permissions=permissions,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
            version=self.version,
        )
