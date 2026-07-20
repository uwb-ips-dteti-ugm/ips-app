from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.dto.common import MessageResponse, PaginatedResponse
from ips_app.presentation.http.dto.permission import PermissionResponse
from ips_app.presentation.http.dto.role import (
    CreateRoleRequest,
    RolePermissionIdsRequest,
    RoleResponse,
    UpdateRolePreferencesRequest,
    UpdateRoleRequest,
)
from ips_app.presentation.http.handlers.role import RoleHandler
from ips_app.presentation.http.middlewares.auth_jwt import get_claims
from ips_app.presentation.http.middlewares.logger import logger
from ips_app.presentation.http.middlewares.permission_check import permission_check


def create_router(
    handler: RoleHandler,
    role_usecase: RoleUsecase,
    log: LeveledLogger,
) -> APIRouter:
    guard_manage = permission_check(["role/manage"], role_usecase)
    guard_view = permission_check(["role/view"], role_usecase)
    guard_delete = permission_check(["role/delete"], role_usecase)

    router = APIRouter(prefix="/roles", tags=["Role"])

    @router.post(
        "",
        response_model=RoleResponse,
        dependencies=[logger(log, "RoleRoutes/post_role"), guard_manage],
    )
    async def post_role(
        request: CreateRoleRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> RoleResponse:
        return await handler.post_role(request, claims)

    @router.get(
        "",
        response_model=PaginatedResponse[RoleResponse],
        dependencies=[logger(log, "RoleRoutes/get_roles"), guard_view],
    )
    async def get_roles(
        page: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        search: Optional[str] = Query(None),
    ) -> PaginatedResponse[RoleResponse]:
        return await handler.get_roles(page, limit, search)

    @router.get(
        "/default",
        response_model=RoleResponse,
        dependencies=[logger(log, "RoleRoutes/get_default_role"), guard_view],
    )
    async def get_default_role() -> RoleResponse:
        return await handler.get_default_role()

    @router.get(
        "/{role_id}",
        response_model=RoleResponse,
        dependencies=[logger(log, "RoleRoutes/get_role"), guard_view],
    )
    async def get_role(role_id: str) -> RoleResponse:
        return await handler.get_role(role_id)

    @router.get(
        "/{role_id}/permissions",
        response_model=List[PermissionResponse],
        dependencies=[logger(log, "RoleRoutes/get_role_permissions"), guard_view],
    )
    async def get_role_permissions(role_id: str) -> List[PermissionResponse]:
        return await handler.get_role_permissions(role_id)

    @router.patch(
        "/{role_id}",
        response_model=RoleResponse,
        dependencies=[logger(log, "RoleRoutes/patch_role"), guard_manage],
    )
    async def patch_role(
        role_id: str,
        request: UpdateRoleRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> RoleResponse:
        return await handler.patch_role(role_id, request, claims)

    @router.patch(
        "/{role_id}/default",
        response_model=RoleResponse,
        dependencies=[logger(log, "RoleRoutes/patch_default_role"), guard_manage],
    )
    async def patch_default_role(
        role_id: str,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> RoleResponse:
        return await handler.patch_default_role(role_id, claims)

    @router.patch(
        "/{role_id}/preferences",
        response_model=RoleResponse,
        dependencies=[logger(log, "RoleRoutes/patch_role_preferences"), guard_manage],
    )
    async def patch_role_preferences(
        role_id: str,
        request: UpdateRolePreferencesRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> RoleResponse:
        return await handler.patch_role_preferences(role_id, request, claims)

    @router.delete(
        "/{role_id}",
        response_model=MessageResponse,
        dependencies=[logger(log, "RoleRoutes/delete_role"), guard_delete],
    )
    async def delete_role(role_id: str) -> MessageResponse:
        return await handler.delete_role(role_id)

    @router.post(
        "/{role_id}/permissions",
        response_model=RoleResponse,
        dependencies=[logger(log, "RoleRoutes/post_role_permissions"), guard_manage],
    )
    async def post_role_permissions(
        role_id: str,
        request: RolePermissionIdsRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> RoleResponse:
        return await handler.post_role_permissions(role_id, request, claims)

    @router.delete(
        "/{role_id}/permissions",
        response_model=RoleResponse,
        dependencies=[logger(log, "RoleRoutes/delete_role_permissions"), guard_manage],
    )
    async def delete_role_permissions(
        role_id: str,
        request: RolePermissionIdsRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> RoleResponse:
        return await handler.delete_role_permissions(role_id, request, claims)

    return router
