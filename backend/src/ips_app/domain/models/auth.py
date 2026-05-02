from datetime import datetime, timezone
from typing import Optional, Annotated, Any
from pydantic import BaseModel, Field
from ips_app.domain.models.user import User


class Auth(BaseModel):
    """
    Pure Domain Model for Auth.
    Decoupled from Beanie/MongoDB.
    """
    id: Optional[Any] = None
    user: Optional[User] = None
    username: str
    password_hash: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = 0
