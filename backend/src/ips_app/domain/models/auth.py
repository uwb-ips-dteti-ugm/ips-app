from datetime import datetime, timezone
from typing import Optional, Annotated
from beanie import Document, Indexed, Link
from pydantic import Field, EmailStr
from ips_app.domain.models.user import User

class Auth(Document):
    user: Link[User]
    username: Annotated[str, Indexed(unique=True)]
    password_hash: str
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = Field(default=0)

    class Settings:
        name = "auths"
