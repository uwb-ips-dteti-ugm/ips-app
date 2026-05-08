from typing import Optional

from fastapi import APIRouter, Request

from ips_app.controllers.http.dto.common import ErrorResponse
from ips_app.controllers.http.dto.permission import (
    AddPermissionRequest,
    PermissionResponse,
    PermissionsResponse,
    SetPermissionRequest,
)
from ips_app.controllers.http.handlers.permission import PermissionHandler
from ips_app.controllers.http.middlewares.feature_guard import feature_guard
from ips_app.controllers.http.middlewares.logger import logger
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driving.http.user import UserHTTP


def create_router(
    handler: PermissionHandler,
    user_service: UserHTTP,
    log: GenericLogging,
) -> APIRouter:
    guard_manage = feature_guard("permission/manage", user_service)
    guard_view = feature_guard("permission/view", user_service)
    guard_delete = feature_guard("permission/delete", user_service)

    router = APIRouter(
        prefix="/permissions",
        tags=["Permission"],
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
        response_model=PermissionResponse,
        dependencies=[
            logger(
                log,
                tag="PermissionRoutes.post_permission",
                msg_2xx="Permission created successfully",
                msg_4xx="Permission creation rejected",
                msg_5xx="Permission creation failed",
            ),
            guard_manage,
        ],
    )
    async def post_permission(request: AddPermissionRequest):
        return await handler.post_permission(request)

    @router.get(
        "",
        response_model=PermissionsResponse,
        dependencies=[
            logger(
                log,
                tag="PermissionRoutes.get_permissions",
                msg_2xx="Permissions fetched successfully",
                msg_4xx="Permissions fetch rejected",
                msg_5xx="Permissions fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_permissions(
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
    ):
        return await handler.get_permissions(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search,
        )

    @router.get(
        "/{permission_id}",
        response_model=PermissionResponse,
        dependencies=[
            logger(
                log,
                tag="PermissionRoutes.get_permission",
                msg_2xx="Permission fetched successfully",
                msg_4xx="Permission fetch rejected",
                msg_5xx="Permission fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_permission(permission_id: str):
        return await handler.get_permission(permission_id)

    @router.patch(
        "/{permission_id}",
        response_model=PermissionResponse,
        dependencies=[
            logger(
                log,
                tag="PermissionRoutes.patch_permission",
                msg_2xx="Permission updated successfully",
                msg_4xx="Permission update rejected",
                msg_5xx="Permission update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_permission(permission_id: str, request: SetPermissionRequest):
        return await handler.patch_permission(permission_id, request)

    @router.patch(
        "/{permission_id}/preferences",
        response_model=PermissionResponse,
        dependencies=[
            logger(
                log,
                tag="PermissionRoutes.patch_permission_preferences",
                msg_2xx="Permission preferences updated successfully",
                msg_4xx="Permission preferences update rejected",
                msg_5xx="Permission preferences update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_permission_preferences(permission_id: str, request: Request):
        return await handler.patch_permission_preferences(permission_id, request)

    @router.delete(
        "/{permission_id}",
        dependencies=[
            logger(
                log,
                tag="PermissionRoutes.delete_permission",
                msg_2xx="Permission deleted successfully",
                msg_4xx="Permission deletion rejected",
                msg_5xx="Permission deletion failed",
            ),
            guard_delete,
        ],
    )
    async def delete_permission(permission_id: str):
        return await handler.delete_permission(permission_id)

    return router
