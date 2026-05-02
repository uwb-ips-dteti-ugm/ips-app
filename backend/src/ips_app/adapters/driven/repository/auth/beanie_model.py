from datetime import datetime, timezone
from typing import Optional, Annotated, Any
from beanie import Document, Indexed, Link
from pydantic import Field
from ips_app.domain.models.auth import Auth
from ips_app.domain.models.user import User
from ips_app.adapters.driven.repository.user.beanie_model import UserDocument


class AuthDocument(Document):
    user: Optional[Link[UserDocument]] = None
    username: Optional[Annotated[str, Indexed(unique=True)]] = None
    password_hash: Optional[str] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = Field(default=0)

    class Settings:
        name = "auths"

    def to_domain(self) -> Auth:
        user_domain = None
        if self.user:
            if isinstance(self.user, UserDocument):
                user_domain = self.user.to_domain()
            elif hasattr(self.user, "ref") and self.user.ref:
                user_domain = User(id=self.user.ref.id, name="", role=None) # type: ignore
            elif hasattr(self.user, "value") and self.user.value:
                user_domain = self.user.value.to_domain()

        return Auth(
            id=self.id,
            user=user_domain,
            username=self.username or "",
            password_hash=self.password_hash or "",
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
            version=self.version,
        )
