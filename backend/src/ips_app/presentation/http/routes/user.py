from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.models.user import UserAccessTokenClaims, UserStatus
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.dto.common import MessageResponse, PaginatedResponse
from ips_app.presentation.http.dto.permission import PermissionResponse
from ips_app.presentation.http.dto.user import (
    UpdateUserInfoRequest,
    UpdateUserPreferencesRequest,
    UpdateUserRoleRequest,
    UpdateUserStatusRequest,
    UserResponse,
)
from ips_app.presentation.http.handlers.user import UserHandler
from ips_app.presentation.http.middlewares.auth_jwt import get_claims
from ips_app.presentation.http.middlewares.logger import logger
from ips_app.presentation.http.middlewares.permission_check import (
    authorization_check,
    permission_check,
)


def _require_claims(claims: Optional[UserAccessTokenClaims]) -> UserAccessTokenClaims:
    if claims is None:
        raise HTTPException(status_code=401, detail="Please sign in to continue.")
    return claims


def create_router(
    handler: UserHandler,
    role_usecase: RoleUsecase,
    log: LeveledLogger,
) -> APIRouter:
    guard_authorized = authorization_check()
    guard_manage = permission_check(["user/manage"], role_usecase)
    guard_view = permission_check(["user/view"], role_usecase)
    guard_delete = permission_check(["user/delete"], role_usecase)

    router = APIRouter(prefix="/users", tags=["User"])

    @router.get(
        "/me",
        response_model=UserResponse,
        dependencies=[logger(log, "UserRoutes/get_user_me"), guard_authorized],
    )
    async def get_user_me(
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> UserResponse:
        return await handler.get_user(_require_claims(claims).user_id)

    @router.get(
        "/me/permissions",
        response_model=List[PermissionResponse],
        dependencies=[logger(log, "UserRoutes/get_user_me_permissions"), guard_authorized],
    )
    async def get_user_me_permissions(
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> List[PermissionResponse]:
        return await handler.get_user_permissions(_require_claims(claims).user_id)

    @router.patch(
        "/me/info",
        response_model=UserResponse,
        dependencies=[logger(log, "UserRoutes/patch_user_me_info"), guard_authorized],
    )
    async def patch_user_me_info(
        request: UpdateUserInfoRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> UserResponse:
        user_id = _require_claims(claims).user_id
        return await handler.patch_user_info(user_id, request, claims)

    @router.patch(
        "/me/preferences",
        response_model=UserResponse,
        dependencies=[logger(log, "UserRoutes/patch_user_me_preferences"), guard_authorized],
    )
    async def patch_user_me_preferences(
        request: UpdateUserPreferencesRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> UserResponse:
        user_id = _require_claims(claims).user_id
        return await handler.patch_user_preferences(user_id, request, claims)

    @router.get(
        "",
        response_model=PaginatedResponse[UserResponse],
        dependencies=[logger(log, "UserRoutes/get_users"), guard_view],
    )
    async def get_users(
        page: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        search: Optional[str] = Query(None),
        role_id: Optional[str] = Query(None),
        status: Optional[UserStatus] = Query(None),
    ) -> PaginatedResponse[UserResponse]:
        return await handler.get_users(page, limit, search, role_id, status)

    @router.get(
        "/{user_id}",
        response_model=UserResponse,
        dependencies=[logger(log, "UserRoutes/get_user"), guard_view],
    )
    async def get_user(user_id: str) -> UserResponse:
        return await handler.get_user(user_id)

    @router.get(
        "/{user_id}/permissions",
        response_model=List[PermissionResponse],
        dependencies=[logger(log, "UserRoutes/get_user_permissions"), guard_view],
    )
    async def get_user_permissions(user_id: str) -> List[PermissionResponse]:
        return await handler.get_user_permissions(user_id)

    @router.patch(
        "/{user_id}/info",
        response_model=UserResponse,
        dependencies=[logger(log, "UserRoutes/patch_user_info"), guard_manage],
    )
    async def patch_user_info(
        user_id: str,
        request: UpdateUserInfoRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> UserResponse:
        return await handler.patch_user_info(user_id, request, claims)

    @router.patch(
        "/{user_id}/preferences",
        response_model=UserResponse,
        dependencies=[logger(log, "UserRoutes/patch_user_preferences"), guard_manage],
    )
    async def patch_user_preferences(
        user_id: str,
        request: UpdateUserPreferencesRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> UserResponse:
        return await handler.patch_user_preferences(user_id, request, claims)

    @router.patch(
        "/{user_id}/role",
        response_model=UserResponse,
        dependencies=[logger(log, "UserRoutes/patch_user_role"), guard_manage],
    )
    async def patch_user_role(
        user_id: str,
        request: UpdateUserRoleRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> UserResponse:
        return await handler.patch_user_role(user_id, request, claims)

    @router.patch(
        "/{user_id}/status",
        response_model=UserResponse,
        dependencies=[logger(log, "UserRoutes/patch_user_status"), guard_manage],
    )
    async def patch_user_status(
        user_id: str,
        request: UpdateUserStatusRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> UserResponse:
        return await handler.patch_user_status(user_id, request, claims)

    @router.delete(
        "/{user_id}",
        response_model=MessageResponse,
        dependencies=[logger(log, "UserRoutes/delete_user"), guard_delete],
    )
    async def delete_user(user_id: str) -> MessageResponse:
        return await handler.delete_user(user_id)

    return router
