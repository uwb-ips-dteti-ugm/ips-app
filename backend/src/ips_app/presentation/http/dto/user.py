from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.domain.models.user import User, UserStatus
from ips_app.presentation.http.dto.common import AuditedResponse, stringify_id
from ips_app.presentation.http.dto.role import RoleResponse


class UpdateUserInfoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    bio: Optional[str] = None
    username: Optional[str] = None


class UpdateUserPreferencesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    preferences: Dict[str, Any]


class UpdateUserRoleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role_id: str = Field(..., examples=["665f1b2e8f1b2e8f1b2e8f1b"])


class UpdateUserStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: UserStatus


class UserResponse(AuditedResponse):
    id: str
    role: RoleResponse
    name: str
    bio: str
    status: UserStatus
    username: str
    preferences: Dict[str, Any]

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        return cls(
            id=str(user.id),
            role=RoleResponse.from_domain(user.role),
            name=user.name,
            bio=user.bio,
            status=user.status,
            username=user.username,
            preferences=user.preferences,
            created_at=user.created_at,
            created_by=stringify_id(user.created_by),
            updated_at=user.updated_at,
            updated_by=stringify_id(user.updated_by),
        )
