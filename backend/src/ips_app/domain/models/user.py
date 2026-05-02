from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from ips_app.domain.models.role import Role


class UserState(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    DND = "dnd"


class UserStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class User(BaseModel):
    id: Optional[Any] = None
    role: Optional[Role] = None
    name: str
    bio: str = ""
    state: UserState = UserState.OFFLINE
    status: UserStatus = UserStatus.ACTIVE
    preferences: Dict[str, Any] = Field(default_factory=dict)

    last_signed_in_at: Optional[datetime] = None
    last_refreshed_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    version: int = 0


class UserAccessTokenClaims(BaseModel):
    user_id: str
    name: str
    role_id: str


class UserRefreshTokenClaims(BaseModel):
    user_id: str
