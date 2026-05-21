from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.controllers.http.dto.common import PaginationMeta
from ips_app.domain.models.permission import Permission
from ips_app.utils.validator import validate_description, validate_resource_name


class AddPermissionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., examples=["user/view"])
    description: str = Field("", examples=["Ability to view users"])

    def validate_fields(self) -> None:
        validate_resource_name(self.name)
        validate_description(self.description)


class SetPermissionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(None, examples=["user/manage"])
    description: Optional[str] = Field(None, examples=["Ability to manage users"])

    def validate_fields(self) -> None:
        if self.name is not None:
            validate_resource_name(self.name)
        if self.description is not None:
            validate_description(self.description)


class PermissionResponse(BaseModel):
    id: str = Field(..., examples=["507f1f77bcf86cd799439011"])
    name: str = Field(..., examples=["user/view"])
    description: str = Field(..., examples=["Ability to view users"])
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_domain(cls, permission: Permission) -> PermissionResponse:
        return cls(
            id=str(permission.id),
            name=permission.name,
            description=permission.description,
            preferences=permission.preferences,
            created_at=permission.created_at,
            updated_at=permission.updated_at,
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
            data=[PermissionResponse.from_domain(permission) for permission in items],
            meta=PaginationMeta(page=page, limit=limit, total=total),
        )
