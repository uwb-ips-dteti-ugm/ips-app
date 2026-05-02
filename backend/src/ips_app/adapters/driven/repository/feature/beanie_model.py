from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Annotated
from beanie import Document, Indexed, Link
from pydantic import Field
from ips_app.domain.models.feature import Feature
from ips_app.domain.models.permission import Permission
from ips_app.adapters.driven.repository.permission.beanie_model import PermissionDocument


class FeatureDocument(Document):
    name: Optional[Annotated[str, Indexed(unique=True)]] = None
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
        perms: List[Permission] = []
        for p in self.permissions:
            if isinstance(p, PermissionDocument):
                perms.append(p.to_domain())
            elif hasattr(p, "ref") and p.ref:
                perms.append(Permission(id=p.ref.id, name=""))
            elif hasattr(p, "value") and p.value:
                perms.append(p.value.to_domain())

        return Feature(
            id=self.id,
            name=self.name or "",
            description=self.description,
            preferences=self.preferences,
            permissions=perms,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
            version=self.version,
        )
