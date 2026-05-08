from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, Optional

from beanie import Document, Indexed, Link
from pydantic import Field
from pymongo import IndexModel

from ips_app.adapters.repository.role.beanie_model import RoleDocument
from ips_app.domain.models.role import Role
from ips_app.domain.models.user import User, UserAuth, UserState, UserStatus


class UserDocument(Document):
    role: Optional[Link[RoleDocument]] = None
    name: Annotated[str, Indexed()]
    bio: str = Field(default="")
    auths: List[UserAuth] = Field(default_factory=list)
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
            [("role.$id", 1)],
            IndexModel(
                [("auths.username", 1)],
                unique=True,
                sparse=True,
                name="unique_user_auth_username",
            ),
        ]

    def to_domain(self) -> User:
        role = None
        if self.role:
            if isinstance(self.role, RoleDocument):
                role = self.role.to_domain()
            elif role_ref := getattr(self.role, "ref", None):
                role = Role(id=role_ref.id, name="")
            elif role_value := getattr(self.role, "value", None):
                role = role_value.to_domain()

        return User(
            id=self.id,
            role=role,
            name=self.name,
            bio=self.bio,
            auths=self.auths,
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
