from typing import List, Optional

from fastapi import APIRouter, Request

from ips_app_old.controllers.http.dto.common import ErrorResponse, PermissionIdsRequest
from ips_app_old.controllers.http.dto.permission import PermissionResponse
from ips_app_old.controllers.http.dto.role import (
    AddRoleRequest,
    RoleResponse,
    RolesResponse,
    SetRoleRequest,
)
from ips_app_old.controllers.http.handlers.role import RoleHandler
from ips_app_old.controllers.http.middlewares.feature_guard import feature_guard
from ips_app_old.controllers.http.middlewares.logger import logger
from ips_app_old.domain.ports.driven.logging.generic import GenericLogging
from ips_app_old.domain.ports.driving.http.user import UserHTTP


def create_router(
    handler: RoleHandler,
    user_service: UserHTTP,
    log: GenericLogging,
) -> APIRouter:
    guard_manage = feature_guard("role/manage", user_service)
    guard_view = feature_guard("role/view", user_service)
    guard_delete = feature_guard("role/delete", user_service)

    router = APIRouter(
        prefix="/roles",
        tags=["Role"],
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
        response_model=RoleResponse,
        dependencies=[
            logger(
                log,
                tag="RoleRoutes.post_role",
                msg_2xx="Role created successfully",
                msg_4xx="Role creation rejected",
                msg_5xx="Role creation failed",
            ),
            guard_manage,
        ],
    )
    async def post_role(request: AddRoleRequest):
        return await handler.post_role(request)

    @router.get(
        "",
        response_model=RolesResponse,
        dependencies=[
            logger(
                log,
                tag="RoleRoutes.get_roles",
                msg_2xx="Roles fetched successfully",
                msg_4xx="Roles fetch rejected",
                msg_5xx="Roles fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_roles(
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
    ):
        return await handler.get_roles(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search,
        )

    @router.get(
        "/{role_id}",
        response_model=RoleResponse,
        dependencies=[
            logger(
                log,
                tag="RoleRoutes.get_role",
                msg_2xx="Role fetched successfully",
                msg_4xx="Role fetch rejected",
                msg_5xx="Role fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_role(role_id: str):
        return await handler.get_role(role_id)

    @router.patch(
        "/{role_id}",
        response_model=RoleResponse,
        dependencies=[
            logger(
                log,
                tag="RoleRoutes.patch_role",
                msg_2xx="Role updated successfully",
                msg_4xx="Role update rejected",
                msg_5xx="Role update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_role(role_id: str, request: SetRoleRequest):
        return await handler.patch_role(role_id, request)

    @router.patch(
        "/{role_id}/preferences",
        response_model=RoleResponse,
        dependencies=[
            logger(
                log,
                tag="RoleRoutes.patch_role_preferences",
                msg_2xx="Role preferences updated successfully",
                msg_4xx="Role preferences update rejected",
                msg_5xx="Role preferences update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_role_preferences(role_id: str, request: Request):
        return await handler.patch_role_preferences(role_id, request)

    @router.delete(
        "/{role_id}",
        dependencies=[
            logger(
                log,
                tag="RoleRoutes.delete_role",
                msg_2xx="Role deleted successfully",
                msg_4xx="Role deletion rejected",
                msg_5xx="Role deletion failed",
            ),
            guard_delete,
        ],
    )
    async def delete_role(role_id: str):
        return await handler.delete_role(role_id)

    @router.post(
        "/{role_id}/permissions",
        response_model=RoleResponse,
        dependencies=[
            logger(
                log,
                tag="RoleRoutes.post_role_permissions",
                msg_2xx="Role permissions added successfully",
                msg_4xx="Role permissions add rejected",
                msg_5xx="Role permissions add failed",
            ),
            guard_manage,
        ],
    )
    async def post_role_permissions(role_id: str, request: PermissionIdsRequest):
        return await handler.post_role_permissions(role_id, request)

    @router.delete(
        "/{role_id}/permissions",
        response_model=RoleResponse,
        dependencies=[
            logger(
                log,
                tag="RoleRoutes.delete_role_permissions",
                msg_2xx="Role permissions removed successfully",
                msg_4xx="Role permissions removal rejected",
                msg_5xx="Role permissions removal failed",
            ),
            guard_manage,
        ],
    )
    async def delete_role_permissions(role_id: str, request: PermissionIdsRequest):
        return await handler.delete_role_permissions(role_id, request)

    @router.get(
        "/{role_id}/permissions",
        response_model=List[PermissionResponse],
        dependencies=[
            logger(
                log,
                tag="RoleRoutes.get_role_permissions",
                msg_2xx="Role permissions fetched successfully",
                msg_4xx="Role permissions fetch rejected",
                msg_5xx="Role permissions fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_role_permissions(role_id: str):
        return await handler.get_role_permissions(role_id)

    return router
