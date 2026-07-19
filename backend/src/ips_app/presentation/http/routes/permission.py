from typing import Optional

from fastapi import APIRouter, Depends, Query

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.dto.common import MessageResponse, PaginatedResponse
from ips_app.presentation.http.dto.permission import (
    CreatePermissionRequest,
    PermissionResponse,
    UpdatePermissionPreferencesRequest,
    UpdatePermissionRequest,
)
from ips_app.presentation.http.handlers.permission import PermissionHandler
from ips_app.presentation.http.middlewares.auth_jwt import get_claims
from ips_app.presentation.http.middlewares.logger import logger
from ips_app.presentation.http.middlewares.permission_check import permission_check


def create_router(
    handler: PermissionHandler,
    role_usecase: RoleUsecase,
    log: LeveledLogger,
) -> APIRouter:
    guard_manage = permission_check(["permission/manage"], role_usecase)
    guard_view = permission_check(["permission/view"], role_usecase)
    guard_delete = permission_check(["permission/delete"], role_usecase)

    router = APIRouter(prefix="/permissions", tags=["Permission"])

    @router.post(
        "",
        response_model=PermissionResponse,
        dependencies=[logger(log, "PermissionRoutes/post_permission"), guard_manage],
    )
    async def post_permission(
        request: CreatePermissionRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> PermissionResponse:
        return await handler.post_permission(request, claims)

    @router.get(
        "",
        response_model=PaginatedResponse[PermissionResponse],
        dependencies=[logger(log, "PermissionRoutes/get_permissions"), guard_view],
    )
    async def get_permissions(
        page: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        search: Optional[str] = Query(None),
    ) -> PaginatedResponse[PermissionResponse]:
        return await handler.get_permissions(page, limit, search)

    @router.get(
        "/{permission_id}",
        response_model=PermissionResponse,
        dependencies=[logger(log, "PermissionRoutes/get_permission"), guard_view],
    )
    async def get_permission(permission_id: str) -> PermissionResponse:
        return await handler.get_permission(permission_id)

    @router.patch(
        "/{permission_id}",
        response_model=PermissionResponse,
        dependencies=[logger(log, "PermissionRoutes/patch_permission"), guard_manage],
    )
    async def patch_permission(
        permission_id: str,
        request: UpdatePermissionRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> PermissionResponse:
        return await handler.patch_permission(permission_id, request, claims)

    @router.patch(
        "/{permission_id}/preferences",
        response_model=PermissionResponse,
        dependencies=[
            logger(log, "PermissionRoutes/patch_permission_preferences"),
            guard_manage,
        ],
    )
    async def patch_permission_preferences(
        permission_id: str,
        request: UpdatePermissionPreferencesRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> PermissionResponse:
        return await handler.patch_permission_preferences(permission_id, request, claims)

    @router.delete(
        "/{permission_id}",
        response_model=MessageResponse,
        dependencies=[logger(log, "PermissionRoutes/delete_permission"), guard_delete],
    )
    async def delete_permission(permission_id: str) -> MessageResponse:
        return await handler.delete_permission(permission_id)

    return router
