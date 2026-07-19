from datetime import datetime, timezone
from enum import StrEnum
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field
from ips_app.domain.models.role import Role


class UserAuthType(StrEnum):
    PASSWORD = "password"


class UserPasswordAuth(BaseModel):
    type: Literal[UserAuthType.PASSWORD] = UserAuthType.PASSWORD
    username: str
    password_hash: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None


UserAuth = Annotated[
    Union[
        UserPasswordAuth,
    ],
    Field(discriminator="type"),
]


class UserStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class User(BaseModel):
    id: Optional[Any] = None
    role: Role
    name: str
    bio: str = ""
    auths: List[UserAuth] = Field(default_factory=list)
    status: UserStatus = UserStatus.ACTIVE
    preferences: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[Any] = None

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
