from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.controllers.http.dto.common import PaginationMeta
from ips_app.domain.models.role import Role
from ips_app.domain.models.user import User, UserState, UserStatus
from ips_app.utils.validator import (
    validate_bio,
    validate_name,
    validate_non_empty_string,
)


class SetUserInfoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(None, examples=["Johnny Doe"])
    bio: Optional[str] = Field(
        None,
        examples=["Software Engineer and Tech Enthusiast"],
    )

    def validate_fields(self) -> None:
        if self.name is not None:
            validate_name(self.name)
        if self.bio is not None:
            validate_bio(self.bio)


class SetUserRoleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_id: str = Field(..., examples=["507f1f77bcf86cd799439011"])

    def validate_fields(self) -> None:
        validate_non_empty_string(self.role_id, "role_id")


class SetUserStateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: UserState = Field(..., examples=[UserState.ONLINE])


class SetUserStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: UserStatus = Field(..., examples=[UserStatus.ACTIVE])


class RoleSummaryResponse(BaseModel):
    id: str = Field(..., examples=["507f1f77bcf86cd799439011"])
    name: str = Field(..., examples=["admin"])
    description: str = Field(..., examples=["Administrator role"])
    is_default: bool = Field(..., examples=[False])

    @classmethod
    def from_domain(cls, role: Role) -> RoleSummaryResponse:
        return cls(
            id=str(role.id),
            name=role.name,
            description=role.description,
            is_default=role.is_default,
        )


class UserResponse(BaseModel):
    id: str = Field(..., examples=["507f1f77bcf86cd799439011"])
    name: str = Field(..., examples=["John Doe"])
    username: Optional[str] = Field(None, examples=["johndoe"])
    bio: str = Field(..., examples=["Software Engineer"])
    state: UserState = Field(..., examples=[UserState.ONLINE])
    status: UserStatus = Field(..., examples=[UserStatus.ACTIVE])
    role: Optional[RoleSummaryResponse] = None
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        examples=[{"theme": "dark"}],
    )
    last_signed_in_at: Optional[datetime] = None
    last_refreshed_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    version: int = Field(..., examples=[1])

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls(
            id=str(user.id),
            name=user.name,
            username=user.password_auth.username if user.password_auth else None,
            bio=user.bio,
            state=user.state,
            status=user.status,
            role=RoleSummaryResponse.from_domain(user.role) if user.role else None,
            preferences=user.preferences,
            last_signed_in_at=user.last_signed_in_at,
            last_refreshed_at=user.last_refreshed_at,
            last_activity_at=user.last_activity_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            version=user.version,
        )


class UsersResponse(BaseModel):
    data: List[UserResponse]
    meta: PaginationMeta

    @classmethod
    def from_domain(
        cls,
        items: List[User],
        page: int,
        limit: int,
        total: int,
    ) -> UsersResponse:
        return cls(
            data=[UserResponse.from_domain(user) for user in items],
            meta=PaginationMeta(page=page, limit=limit, total=total),
        )
