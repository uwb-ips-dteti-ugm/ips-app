from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Annotated
from beanie import Document, Indexed, Link
from pydantic import Field
from ips_app.domain.models.user import User, UserState, UserStatus
from ips_app.domain.models.role import Role
from ips_app.adapters.driven.repository.role.beanie_model import RoleDocument


class UserDocument(Document):
    role: Optional[Link[RoleDocument]] = None
    name: Optional[Annotated[str, Indexed()]] = None
    bio: str = Field(default="")
    state: UserState = Field(default=UserState.OFFLINE)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    preferences: Dict[str, Any] = Field(default_factory=dict)

    last_signed_in_at: Optional[datetime] = None
    last_refreshed_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = Field(default=0)

    class Settings:
        name = "users"
        indexes = [
            [("status", 1)],
            [("state", 1)],
        ]

    def to_domain(self) -> User:
        role_domain = None
        if self.role:
            if isinstance(self.role, RoleDocument):
                role_domain = self.role.to_domain()
            elif hasattr(self.role, "ref") and self.role.ref:
                role_domain = Role(id=self.role.ref.id, name="")
            elif hasattr(self.role, "value") and self.role.value:
                role_domain = self.role.value.to_domain()

        return User(
            id=self.id,
            role=role_domain,
            name=self.name or "",
            bio=self.bio,
            state=self.state,
            status=self.status,
            preferences=self.preferences,
            last_signed_in_at=self.last_signed_in_at,
            last_refreshed_at=self.last_refreshed_at,
            last_activity_at=self.last_activity_at,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
            version=self.version,
        )
