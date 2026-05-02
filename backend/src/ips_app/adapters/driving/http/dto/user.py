from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from ips_app.domain.models.user import User, UserState, UserStatus
from ips_app.domain.models.role import Role
from ips_app.adapters.driving.http.dto.common import PaginationMeta
from ips_app.utils.validator import validate_name, validate_bio

class SetUserInfoRequest(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None

    def validate_fields(self) -> None:
        if self.name is not None:
            validate_name(self.name)
        if self.bio is not None:
            validate_bio(self.bio)

class SetUserRoleRequest(BaseModel):
    role_id: str

    def validate_fields(self) -> None:
        if not self.role_id.strip():
            raise ValueError("role_id must not be empty.")

class SetUserStateRequest(BaseModel):
    state: UserState

class SetUserStatusRequest(BaseModel):
    status: UserStatus

class RoleSummaryResponse(BaseModel):
    id: str
    name: str
    description: str
    is_default: bool

    @classmethod
    def from_domain(cls, role: Role) -> RoleSummaryResponse:
        return cls(
            id=str(role.id),
            name=role.name,
            description=role.description,
            is_default=role.is_default,
        )

class UserResponse(BaseModel):
    id: str
    name: str
    bio: str
    state: UserState
    status: UserStatus
    role: Optional[RoleSummaryResponse] = None
    preferences: Dict[str, Any]
    last_signed_in_at: Optional[datetime]
    last_refreshed_at: Optional[datetime]
    last_activity_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    version: int

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls(
            id=str(user.id),
            name=user.name,
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
            data=[UserResponse.from_domain(u) for u in items],
            meta=PaginationMeta(page=page, limit=limit, total=total),
        )
