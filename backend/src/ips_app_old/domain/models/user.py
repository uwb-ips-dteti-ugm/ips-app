from datetime import datetime, timezone
from enum import StrEnum
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field
from ips_app_old.domain.models.role import Role


class UserAuthType(StrEnum):
    PASSWORD = "password"


class UserPasswordAuth(BaseModel):
    type: Literal[UserAuthType.PASSWORD] = UserAuthType.PASSWORD
    username: str
    password_hash: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None


UserAuth = Annotated[
    Union[
        UserPasswordAuth,
    ],
    Field(discriminator="type"),
]


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
    auths: List[UserAuth] = Field(default_factory=list)
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

    @property
    def password_auth(self) -> Optional[UserPasswordAuth]:
        return next(
            (
                auth
                for auth in self.auths
                if isinstance(auth, UserPasswordAuth)
            ),
            None,
        )


class UserAccessTokenClaims(BaseModel):
    user_id: str
    name: str
    role_id: str


class UserRefreshTokenClaims(BaseModel):
    user_id: str
