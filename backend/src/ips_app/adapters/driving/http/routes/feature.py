from typing import List, Optional
from fastapi import APIRouter, Request
from ips_app.adapters.driving.http.handler.feature import FeatureHandler
from ips_app.adapters.driving.http.dto.feature import (
    AddFeatureRequest,
    SetFeatureRequest,
    FeatureResponse,
    FeaturesResponse,
)
from ips_app.adapters.driving.http.dto.permission import PermissionResponse
from ips_app.adapters.driving.http.dto.common import PermissionIdsRequest

def create_router(handler: FeatureHandler) -> APIRouter:
    router = APIRouter(prefix="/features")

    @router.post("", response_model=FeatureResponse)
    async def post_feature(request: AddFeatureRequest) -> FeatureResponse:
        return await handler.post_feature(request)

    @router.get("/me/accessible", response_model=List[FeatureResponse])
    async def get_feature_me_accessible() -> List[FeatureResponse]:
        return await handler.get_feature_me_accessible()

    @router.get("", response_model=FeaturesResponse)
    async def get_features(
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> FeaturesResponse:
        return await handler.get_features(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search,
        )

    @router.get("/{feature_id}", response_model=FeatureResponse)
    async def get_feature(feature_id: str) -> FeatureResponse:
        return await handler.get_feature(feature_id)

    @router.get("/{feature_id}/me/can-access", response_model=bool)
    async def get_feature_me_can_access(feature_id: str) -> bool:
        return await handler.get_feature_me_can_access(feature_id)

    @router.patch("/{feature_id}", response_model=FeatureResponse)
    async def patch_feature(feature_id: str, request: SetFeatureRequest) -> FeatureResponse:
        return await handler.patch_feature(feature_id, request)

    @router.patch("/{feature_id}/preferences", response_model=FeatureResponse)
    async def patch_feature_preferences(feature_id: str, request: Request) -> FeatureResponse:
        return await handler.patch_feature_preferences(feature_id, request)

    @router.delete("/{feature_id}")
    async def delete_feature(feature_id: str):
        return await handler.delete_feature(feature_id)

    @router.post("/{feature_id}/permissions", response_model=FeatureResponse)
    async def post_feature_permissions(feature_id: str, request: PermissionIdsRequest) -> FeatureResponse:
        return await handler.post_feature_permissions(feature_id, request)

    @router.delete("/{feature_id}/permissions", response_model=FeatureResponse)
    async def delete_feature_permissions(feature_id: str, request: PermissionIdsRequest) -> FeatureResponse:
        return await handler.delete_feature_permissions(feature_id, request)

    @router.get("/{feature_id}/permissions", response_model=List[PermissionResponse])
    async def get_feature_permissions(feature_id: str) -> List[PermissionResponse]:
        return await handler.get_feature_permissions(feature_id)

    return router
