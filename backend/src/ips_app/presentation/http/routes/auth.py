from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.dto.auth import (
    ChangePasswordRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SignInRequest,
    TokenResponse,
)
from ips_app.presentation.http.dto.common import MessageResponse
from ips_app.presentation.http.dto.user import UserResponse
from ips_app.presentation.http.handlers.auth import AuthHandler
from ips_app.presentation.http.middlewares.auth_jwt import get_claims
from ips_app.presentation.http.middlewares.logger import logger
from ips_app.presentation.http.middlewares.permission_check import (
    authorization_check,
    permission_check,
)


def create_router(
    handler: AuthHandler,
    role_usecase: RoleUsecase,
    log: LeveledLogger,
) -> APIRouter:
    guard_authorized = authorization_check()
    guard_manage = permission_check(["auth/manage"], role_usecase)

    router = APIRouter(prefix="/auth", tags=["Auth"])

    @router.post(
        "/sign-in",
        response_model=TokenResponse,
        dependencies=[logger(log, "AuthRoutes/post_sign_in")],
    )
    async def post_sign_in(request: SignInRequest) -> TokenResponse:
        return await handler.post_sign_in(request)

    @router.post(
        "/refresh-token",
        response_model=TokenResponse,
        dependencies=[logger(log, "AuthRoutes/post_refresh_token")],
    )
    async def post_refresh_token(request: RefreshTokenRequest) -> TokenResponse:
        return await handler.post_refresh_token(request)

    @router.post(
        "/register",
        response_model=UserResponse,
        dependencies=[logger(log, "AuthRoutes/post_register"), guard_manage],
    )
    async def post_register(
        request: RegisterRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> UserResponse:
        return await handler.post_register(request, claims)

    @router.patch(
        "/me/password",
        response_model=MessageResponse,
        dependencies=[logger(log, "AuthRoutes/patch_auth_me_password"), guard_authorized],
    )
    async def patch_auth_me_password(
        request: ChangePasswordRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> MessageResponse:
        if claims is None:
            raise HTTPException(status_code=401, detail="Please sign in to continue.")
        return await handler.patch_auth_me_password(request, claims)

    @router.patch(
        "/{user_id}/password",
        response_model=MessageResponse,
        dependencies=[logger(log, "AuthRoutes/patch_user_password"), guard_manage],
    )
    async def patch_user_password(
        user_id: str,
        request: ResetPasswordRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> MessageResponse:
        return await handler.patch_user_password(user_id, request, claims)

    return router
