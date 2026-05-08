from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from ips_app_old.domain.models.permission import Permission
from ips_app_old.adapters.driving.http.dto.common import PaginationMeta
from ips_app_old.utils.validator import validate_resource_name, validate_description

class AddPermissionRequest(BaseModel):
    name: str = Field(..., examples=["user:view"])
    description: str = Field("", examples=["Ability to view user profiles"])

    def validate_fields(self) -> None:
        validate_resource_name(self.name)
        validate_description(self.description)

class SetPermissionRequest(BaseModel):
    name: Optional[str] = Field(None, examples=["user:manage"])
    description: Optional[str] = Field(None, examples=["Full user management"])

    def validate_fields(self) -> None:
        if self.name is not None:
            validate_resource_name(self.name)
        if self.description is not None:
            validate_description(self.description)

class PermissionResponse(BaseModel):
    id: str = Field(..., examples=["507f1f77bcf86cd799439011"])
    name: str = Field(..., examples=["user:view"])
    description: str = Field(..., examples=["View user profiles"])
    preferences: Dict[str, Any] = Field(default_factory=dict, examples=[{"internal": True}])
    created_at: datetime
    updated_at: Optional[datetime] = None
    version: int = Field(..., examples=[1])

    @classmethod
    def from_domain(cls, permission: Permission) -> PermissionResponse:
        return cls(
            id=str(permission.id),
            name=permission.name,
            description=permission.description,
            preferences=permission.preferences,
            created_at=permission.created_at,
            updated_at=permission.updated_at,
            version=permission.version,
        )

class PermissionsResponse(BaseModel):
    data: List[PermissionResponse]
    meta: PaginationMeta

    @classmethod
    def from_domain(
        cls,
        items: List[Permission],
        page: int,
        limit: int,
        total: int,
    ) -> PermissionsResponse:
        return cls(
            data=[PermissionResponse.from_domain(p) for p in items],
            meta=PaginationMeta(page=page, limit=limit, total=total),
        )
