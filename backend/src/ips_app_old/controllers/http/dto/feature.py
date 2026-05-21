from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app_old.controllers.http.dto.common import PaginationMeta
from ips_app_old.controllers.http.dto.permission import PermissionResponse
from ips_app_old.domain.models.feature import Feature
from ips_app_old.utils.validator import validate_description, validate_resource_name


class AddFeatureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., examples=["user/view"])
    description: str = Field("", examples=["Feature gate for user viewing"])

    def validate_fields(self) -> None:
        validate_resource_name(self.name)
        validate_description(self.description)


class SetFeatureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(None, examples=["user/manage"])
    description: Optional[str] = Field(None, examples=["Full feature management"])

    def validate_fields(self) -> None:
        if self.name is not None:
            validate_resource_name(self.name)
        if self.description is not None:
            validate_description(self.description)


class FeatureResponse(BaseModel):
    id: str = Field(..., examples=["507f1f77bcf86cd799439011"])
    name: str = Field(..., examples=["user/view"])
    description: str = Field(..., examples=["User viewing feature gate"])
    permissions: List[PermissionResponse] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        examples=[{"enabled": True}],
    )
    created_at: datetime
    updated_at: Optional[datetime] = None
    version: int = Field(..., examples=[1])

    @classmethod
    def from_domain(cls, feature: Feature) -> FeatureResponse:
        return cls(
            id=str(feature.id),
            name=feature.name,
            description=feature.description,
            permissions=[
                PermissionResponse.from_domain(permission)
                for permission in feature.permissions
            ],
            preferences=feature.preferences,
            created_at=feature.created_at,
            updated_at=feature.updated_at,
            version=feature.version,
        )


class FeaturesResponse(BaseModel):
    data: List[FeatureResponse]
    meta: PaginationMeta

    @classmethod
    def from_domain(
        cls,
        items: List[Feature],
        page: int,
        limit: int,
        total: int,
    ) -> FeaturesResponse:
        return cls(
            data=[FeatureResponse.from_domain(feature) for feature in items],
            meta=PaginationMeta(page=page, limit=limit, total=total),
        )


class FeatureAccessResponse(BaseModel):
    feature_name: str = Field(..., examples=["user/view"])
    can_access: bool = Field(..., examples=[True])
