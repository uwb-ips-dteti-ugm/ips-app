from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.domain.models.role import Role
from ips_app.presentation.http.dto.common import AuditedResponse, stringify_id
from ips_app.presentation.http.dto.permission import PermissionResponse


class CreateRoleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., examples=["operator"])
    description: str = Field("", examples=["Can operate nodes"])
    is_default: bool = False


class UpdateRoleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    description: Optional[str] = None


class UpdateRolePreferencesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    preferences: Dict[str, Any]


class RolePermissionIdsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    permission_ids: List[str]


class RoleResponse(AuditedResponse):
    id: str
    name: str
    description: str
    is_default: bool
    preferences: Dict[str, Any]
    permissions: List[PermissionResponse]

    @classmethod
    def from_domain(cls, role: Role) -> "RoleResponse":
        return cls(
            id=str(role.id),
            name=role.name,
            description=role.description,
            is_default=role.is_default,
            preferences=role.preferences,
            permissions=[PermissionResponse.from_domain(p) for p in role.permissions],
            created_at=role.created_at,
            created_by=stringify_id(role.created_by),
            updated_at=role.updated_at,
            updated_by=stringify_id(role.updated_by),
        )
