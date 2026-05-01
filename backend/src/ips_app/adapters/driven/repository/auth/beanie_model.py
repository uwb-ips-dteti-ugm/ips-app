from datetime import datetime, timezone
from typing import Optional, Annotated
from beanie import Document, Indexed, Link
from pydantic import Field
from ips_app.domain.models.auth import Auth
from ips_app.domain.models.user import User
from ips_app.adapters.driven.repository.user.beanie_model import UserDocument


class AuthDocument(Document):
    user: Link[UserDocument]
    username: Annotated[str, Indexed(unique=True)]
    password_hash: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = Field(default=0)

    class Settings:
        name = "auths"

    def to_domain(self) -> Auth:
        return Auth(
            id=self.id,
            user=self.user.to_domain() if isinstance(self.user, UserDocument) else User(id=self.user.ref.id, name="", role=None),  # type: ignore
            username=self.username,
            password_hash=self.password_hash,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=self.updated_at,
            updated_by=self.updated_by,
            version=self.version,
        )
