from datetime import datetime, timezone
from enum import StrEnum
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field
from ips_app.domain.models.role import Role


class UserStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class User(BaseModel):
    id: Optional[Any] = None
    role: Role
    name: str = Field(..., min_length=1)
    bio: str = Field("", max_length=2000)
    status: UserStatus = UserStatus.ACTIVE
    username: str = Field(..., min_length=1)
    password_hash: str = Field(..., min_length=1)
    preferences: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None


class UserAccessTokenClaims(BaseModel):
    user_id: str
    role_id: str
    name: str


class UserRefreshTokenClaims(BaseModel):
    user_id: str
