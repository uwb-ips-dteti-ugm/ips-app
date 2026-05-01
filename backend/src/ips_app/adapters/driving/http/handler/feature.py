from typing import Optional, List
from fastapi import Request, Response, status
from ips_app.ports.driving.http.feature import FeatureHTTPPort
from ips_app.adapters.driving.http.dto.feature import (
    AddFeatureRequest,
    SetFeatureRequest,
    FeatureResponse,
    FeaturesResponse
)
from ips_app.adapters.driving.http.dto.permission import PermissionResponse
from ips_app.adapters.driving.http.dto.common import PermissionIdsRequest
from ips_app.adapters.driving.http.middleware.auth_jwt import get_claims

class FeatureHandler:
    def __init__(self, service: FeatureHTTPPort):
        self.service = service

    async def post_feature(self, request: AddFeatureRequest) -> FeatureResponse:
        request.validate_fields()
        feature = await self.service.add_feature(
            name=request.name,
            description=request.description
        )
        return FeatureResponse.from_domain(feature)

    async def get_feature(self, feature_id: str) -> FeatureResponse:
        feature = await self.service.get_feature(feature_id)
        return FeatureResponse.from_domain(feature)

    async def get_features(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> FeaturesResponse:
        items, total = await self.service.get_features(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search
        )
        return FeaturesResponse.from_domain(
            items=items,
            page=page,
            limit=limit,
            total=total
        )

    async def patch_feature(
        self,
        feature_id: str,
        request: SetFeatureRequest
    ) -> FeatureResponse:
        request.validate_fields()
        feature = await self.service.set_feature(
            feature_id=feature_id,
            name=request.name,
            description=request.description
        )
        return FeatureResponse.from_domain(feature)

    async def patch_feature_preferences(
        self,
        feature_id: str,
        request: Request
    ) -> FeatureResponse:
        body = await request.body()
        feature = await self.service.set_feature_preferences(
            feature_id=feature_id,
            preferences=body
        )
        return FeatureResponse.from_domain(feature)

    async def delete_feature(self, feature_id: str) -> Response:
        message = await self.service.remove_feature(feature_id)
        return Response(content=message, status_code=status.HTTP_200_OK)

    async def post_feature_permissions(
        self,
        feature_id: str,
        request: PermissionIdsRequest
    ) -> FeatureResponse:
        request.validate_fields()
        feature = await self.service.add_permissions_to_feature(
            feature_id=feature_id,
            permission_ids=request.permission_ids
        )
        return FeatureResponse.from_domain(feature)

    async def delete_feature_permissions(
        self,
        feature_id: str,
        request: PermissionIdsRequest
    ) -> FeatureResponse:
        request.validate_fields()
        feature = await self.service.remove_permissions_from_feature(
            feature_id=feature_id,
            permission_ids=request.permission_ids
        )
        return FeatureResponse.from_domain(feature)

    async def get_feature_permissions(self, feature_id: str) -> List[PermissionResponse]:
        permissions = await self.service.get_feature_permissions(feature_id)
        return [PermissionResponse.from_domain(p) for p in permissions]

    async def get_feature_me_accessible(self) -> List[FeatureResponse]:
        claims = get_claims()
        if not claims:
            return []
        features = await self.service.get_accessible_features(user_id=claims.user_id)
        return [FeatureResponse.from_domain(f) for f in features]

    async def get_feature_me_can_access(self, feature_id: str) -> bool:
        claims = get_claims()
        if not claims:
            return False
        return await self.service.can_access_feature(
            user_id=claims.user_id,
            feature_id=feature_id
        )
