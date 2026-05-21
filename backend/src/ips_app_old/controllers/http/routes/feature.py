from typing import List, Optional

from fastapi import APIRouter, Request

from ips_app_old.controllers.http.dto.common import ErrorResponse, PermissionIdsRequest
from ips_app_old.controllers.http.dto.feature import (
    AddFeatureRequest,
    FeatureResponse,
    FeaturesResponse,
    SetFeatureRequest,
)
from ips_app_old.controllers.http.dto.permission import PermissionResponse
from ips_app_old.controllers.http.handlers.feature import FeatureHandler
from ips_app_old.controllers.http.middlewares.feature_guard import feature_guard
from ips_app_old.controllers.http.middlewares.logger import logger
from ips_app_old.domain.ports.driven.logging.generic import GenericLogging
from ips_app_old.domain.ports.driving.http.user import UserHTTP


def create_router(
    handler: FeatureHandler,
    user_service: UserHTTP,
    log: GenericLogging,
) -> APIRouter:
    guard_manage = feature_guard("feature/manage", user_service)
    guard_view = feature_guard("feature/view", user_service)
    guard_delete = feature_guard("feature/delete", user_service)

    router = APIRouter(
        prefix="/features",
        tags=["Feature"],
        responses={
            400: {"model": ErrorResponse, "description": "Bad Request"},
            401: {"model": ErrorResponse, "description": "Unauthorized"},
            403: {"model": ErrorResponse, "description": "Forbidden"},
            404: {"model": ErrorResponse, "description": "Not Found"},
            409: {"model": ErrorResponse, "description": "Conflict"},
            500: {"model": ErrorResponse, "description": "Internal Server Error"},
        },
    )

    @router.post(
        "",
        response_model=FeatureResponse,
        dependencies=[
            logger(
                log,
                tag="FeatureRoutes.post_feature",
                msg_2xx="Feature created successfully",
                msg_4xx="Feature creation rejected",
                msg_5xx="Feature creation failed",
            ),
            guard_manage,
        ],
    )
    async def post_feature(request: AddFeatureRequest):
        return await handler.post_feature(request)

    @router.get(
        "",
        response_model=FeaturesResponse,
        dependencies=[
            logger(
                log,
                tag="FeatureRoutes.get_features",
                msg_2xx="Features fetched successfully",
                msg_4xx="Features fetch rejected",
                msg_5xx="Features fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_features(
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
    ):
        return await handler.get_features(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search,
        )

    @router.get(
        "/{feature_id}",
        response_model=FeatureResponse,
        dependencies=[
            logger(
                log,
                tag="FeatureRoutes.get_feature",
                msg_2xx="Feature fetched successfully",
                msg_4xx="Feature fetch rejected",
                msg_5xx="Feature fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_feature(feature_id: str):
        return await handler.get_feature(feature_id)

    @router.patch(
        "/{feature_id}",
        response_model=FeatureResponse,
        dependencies=[
            logger(
                log,
                tag="FeatureRoutes.patch_feature",
                msg_2xx="Feature updated successfully",
                msg_4xx="Feature update rejected",
                msg_5xx="Feature update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_feature(feature_id: str, request: SetFeatureRequest):
        return await handler.patch_feature(feature_id, request)

    @router.patch(
        "/{feature_id}/preferences",
        response_model=FeatureResponse,
        dependencies=[
            logger(
                log,
                tag="FeatureRoutes.patch_feature_preferences",
                msg_2xx="Feature preferences updated successfully",
                msg_4xx="Feature preferences update rejected",
                msg_5xx="Feature preferences update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_feature_preferences(feature_id: str, request: Request):
        return await handler.patch_feature_preferences(feature_id, request)

    @router.delete(
        "/{feature_id}",
        dependencies=[
            logger(
                log,
                tag="FeatureRoutes.delete_feature",
                msg_2xx="Feature deleted successfully",
                msg_4xx="Feature deletion rejected",
                msg_5xx="Feature deletion failed",
            ),
            guard_delete,
        ],
    )
    async def delete_feature(feature_id: str):
        return await handler.delete_feature(feature_id)

    @router.post(
        "/{feature_id}/permissions",
        response_model=FeatureResponse,
        dependencies=[
            logger(
                log,
                tag="FeatureRoutes.post_feature_permissions",
                msg_2xx="Feature permissions added successfully",
                msg_4xx="Feature permissions add rejected",
                msg_5xx="Feature permissions add failed",
            ),
            guard_manage,
        ],
    )
    async def post_feature_permissions(
        feature_id: str,
        request: PermissionIdsRequest,
    ):
        return await handler.post_feature_permissions(feature_id, request)

    @router.delete(
        "/{feature_id}/permissions",
        response_model=FeatureResponse,
        dependencies=[
            logger(
                log,
                tag="FeatureRoutes.delete_feature_permissions",
                msg_2xx="Feature permissions removed successfully",
                msg_4xx="Feature permissions removal rejected",
                msg_5xx="Feature permissions removal failed",
            ),
            guard_manage,
        ],
    )
    async def delete_feature_permissions(
        feature_id: str,
        request: PermissionIdsRequest,
    ):
        return await handler.delete_feature_permissions(feature_id, request)

    @router.get(
        "/{feature_id}/permissions",
        response_model=List[PermissionResponse],
        dependencies=[
            logger(
                log,
                tag="FeatureRoutes.get_feature_permissions",
                msg_2xx="Feature permissions fetched successfully",
                msg_4xx="Feature permissions fetch rejected",
                msg_5xx="Feature permissions fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_feature_permissions(feature_id: str):
        return await handler.get_feature_permissions(feature_id)

    return router
