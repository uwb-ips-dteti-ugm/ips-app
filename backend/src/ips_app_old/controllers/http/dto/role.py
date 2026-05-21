from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app_old.controllers.http.dto.common import PaginationMeta
from ips_app_old.controllers.http.dto.permission import PermissionResponse
from ips_app_old.domain.models.role import Role
from ips_app_old.utils.validator import validate_description, validate_resource_name


class AddRoleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., examples=["admin"])
    description: str = Field("", examples=["Administrator with full access"])

    def validate_fields(self) -> None:
        validate_resource_name(self.name)
        validate_description(self.description)


class SetRoleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(None, examples=["superadmin"])
    description: Optional[str] = Field(None, examples=["Root administrator"])

    def validate_fields(self) -> None:
        if self.name is not None:
            validate_resource_name(self.name)
        if self.description is not None:
            validate_description(self.description)


class RoleResponse(BaseModel):
    id: str = Field(..., examples=["507f1f77bcf86cd799439011"])
    name: str = Field(..., examples=["admin"])
    description: str = Field(..., examples=["Administrator role"])
    is_default: bool = Field(..., examples=[False])
    permissions: List[PermissionResponse] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        examples=[{"color": "red"}],
    )
    created_at: datetime
    updated_at: Optional[datetime] = None
    version: int = Field(..., examples=[1])

    @classmethod
    def from_domain(cls, role: Role) -> RoleResponse:
        return cls(
            id=str(role.id),
            name=role.name,
            description=role.description,
            is_default=role.is_default,
            permissions=[
                PermissionResponse.from_domain(permission)
                for permission in role.permissions
            ],
            preferences=role.preferences,
            created_at=role.created_at,
            updated_at=role.updated_at,
            version=role.version,
        )


class RolesResponse(BaseModel):
    data: List[RoleResponse]
    meta: PaginationMeta

    @classmethod
    def from_domain(
        cls,
        items: List[Role],
        page: int,
        limit: int,
        total: int,
    ) -> RolesResponse:
        return cls(
            data=[RoleResponse.from_domain(role) for role in items],
            meta=PaginationMeta(page=page, limit=limit, total=total),
        )
