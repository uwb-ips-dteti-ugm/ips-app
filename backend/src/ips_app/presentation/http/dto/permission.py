from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.domain.models.permission import Permission
from ips_app.presentation.http.dto.common import AuditedResponse, stringify_id


class CreatePermissionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., examples=["user/view"])
    description: str = Field("", examples=["Ability to view users"])


class UpdatePermissionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    description: Optional[str] = None


class UpdatePermissionPreferencesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    preferences: Dict[str, Any]


class PermissionResponse(AuditedResponse):
    id: str
    name: str
    description: str
    preferences: Dict[str, Any]

    @classmethod
    def from_domain(cls, permission: Permission) -> "PermissionResponse":
        return cls(
            id=str(permission.id),
            name=permission.name,
            description=permission.description,
            preferences=permission.preferences,
            created_at=permission.created_at,
            created_by=stringify_id(permission.created_by),
            updated_at=permission.updated_at,
            updated_by=stringify_id(permission.updated_by),
        )
