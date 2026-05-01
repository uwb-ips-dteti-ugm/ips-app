from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from ips_app.domain.models.feature import Feature
from ips_app.adapters.driving.http.dto.common import PaginationMeta
from ips_app.adapters.driving.http.dto.permission import PermissionResponse
from ips_app.utils.validator import validate_resource_name, validate_description

class AddFeatureRequest(BaseModel):
    name: str
    description: str = ""

    def validate_fields(self) -> None:
        validate_resource_name(self.name)
        validate_description(self.description)

class SetFeatureRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    def validate_fields(self) -> None:
        if self.name is not None:
            validate_resource_name(self.name)
        if self.description is not None:
            validate_description(self.description)

class FeatureResponse(BaseModel):
    id: str
    name: str
    description: str
    permissions: List[PermissionResponse]
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    version: int

    @classmethod
    def from_domain(cls, feature: Feature) -> FeatureResponse:
        return cls(
            id=str(feature.id),
            name=feature.name,
            description=feature.description,
            permissions=[PermissionResponse.from_domain(p) for p in feature.permissions],
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
            data=[FeatureResponse.from_domain(f) for f in items],
            meta=PaginationMeta(page=page, limit=limit, total=total),
        )
