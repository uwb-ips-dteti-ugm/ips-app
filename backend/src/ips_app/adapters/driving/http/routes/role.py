from typing import List, Optional
from fastapi import APIRouter, Request
from ips_app.adapters.driving.http.handler.role import RoleHandler
from ips_app.adapters.driving.http.middleware.logger import logger
from ips_app.adapters.driving.http.middleware.feature_guard import feature_guard
from ips_app.ports.driving.http.feature import FeatureHTTPPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.adapters.driving.http.dto.role import (
    AddRoleRequest,
    SetRoleRequest,
    RoleResponse,
    RolesResponse,
)
from ips_app.adapters.driving.http.dto.permission import PermissionResponse
from ips_app.adapters.driving.http.dto.common import PermissionIdsRequest


from ips_app.adapters.driving.http.dto.common import ErrorResponse
...
def create_router(
    handler: RoleHandler,
    feature_service: FeatureHTTPPort,
    log: GenericLoggingPort,
) -> APIRouter:
    logdep = logger(log)
    guard_manage = feature_guard("role/manage", feature_service)
    guard_view = feature_guard("role/view", feature_service)
    guard_delete = feature_guard("role/delete", feature_service)

    router = APIRouter(
        prefix="/roles",
        tags=["Role"],
        responses={
            401: {"model": ErrorResponse, "description": "Unauthorized"},
            403: {"model": ErrorResponse, "description": "Forbidden"},
            404: {"model": ErrorResponse, "description": "Not Found"},
            409: {"model": ErrorResponse, "description": "Conflict"},
            500: {"model": ErrorResponse, "description": "Internal Server Error"},
        },
    )

    @router.post("", response_model=RoleResponse, dependencies=[logdep, guard_manage])
    async def post_role(request: AddRoleRequest) -> RoleResponse:
        return await handler.post_role(request)

    @router.get("", response_model=RolesResponse, dependencies=[logdep, guard_view])
    async def get_roles(
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> RolesResponse:
        return await handler.get_roles(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search,
        )

    @router.get("/{role_id}", response_model=RoleResponse, dependencies=[logdep, guard_view])
    async def get_role(role_id: str) -> RoleResponse:
        return await handler.get_role(role_id)

    @router.patch("/{role_id}", response_model=RoleResponse, dependencies=[logdep, guard_manage])
    async def patch_role(role_id: str, request: SetRoleRequest) -> RoleResponse:
        return await handler.patch_role(role_id, request)

    @router.patch("/{role_id}/preferences", response_model=RoleResponse, dependencies=[logdep, guard_manage])
    async def patch_role_preferences(role_id: str, request: Request) -> RoleResponse:
        return await handler.patch_role_preferences(role_id, request)

    @router.delete("/{role_id}", dependencies=[logdep, guard_delete])
    async def delete_role(role_id: str):
        return await handler.delete_role(role_id)

    @router.post("/{role_id}/permissions", response_model=RoleResponse, dependencies=[logdep, guard_manage])
    async def post_role_permissions(role_id: str, request: PermissionIdsRequest) -> RoleResponse:
        return await handler.post_role_permissions(role_id, request)

    @router.delete("/{role_id}/permissions", response_model=RoleResponse, dependencies=[logdep, guard_manage])
    async def delete_role_permissions(role_id: str, request: PermissionIdsRequest) -> RoleResponse:
        return await handler.delete_role_permissions(role_id, request)

    @router.get("/{role_id}/permissions", response_model=List[PermissionResponse], dependencies=[logdep, guard_view])
    async def get_role_permissions(role_id: str) -> List[PermissionResponse]:
        return await handler.get_role_permissions(role_id)

    return router
