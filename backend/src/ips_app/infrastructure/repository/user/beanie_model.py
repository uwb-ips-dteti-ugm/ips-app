from datetime import datetime, timezone
from typing import Annotated, Any, Dict, Optional

from beanie import Document, Indexed, Link
from pydantic import Field

from ips_app.domain.models.user import User, UserStatus
from ips_app.infrastructure.repository._shared.link import required_link
from ips_app.infrastructure.repository.role.beanie_model import RoleDocument


class UserDocument(Document):
    role: Link[RoleDocument]
    name: Annotated[str, Indexed()]
    bio: str = Field(default="")
    username: Annotated[str, Indexed(unique=True)]
    password_hash: str
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    preferences: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None

    class Settings:
        name = "users"
        indexes = [
            [("status", 1)],
            [("role.$id", 1)],
        ]

    def to_domain(self) -> User:
        role = required_link(self.role, field_name="role")
        return User(
            id=self.id,
            role=role.to_domain(),
            name=self.name,
            bio=self.bio,
            username=self.username,
            password_hash=self.password_hash,
            status=self.status,
            preferences=self.preferences,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
        )
