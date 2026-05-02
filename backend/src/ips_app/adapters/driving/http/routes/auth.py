from fastapi import APIRouter
from ips_app.adapters.driving.http.handler.auth import AuthHandler
from ips_app.adapters.driving.http.middleware.logger import logger
from ips_app.adapters.driving.http.middleware.feature_guard import feature_guard
from ips_app.ports.driving.http.feature import FeatureHTTPPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.adapters.driving.http.dto.auth import (
    SignUpRequest,
    SignInRequest,
    RegisterRequest,
    SetNewPasswordRequest,
    SetNewPasswordWithOldPasswordRequest,
    SetAuthInfoRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from ips_app.adapters.driving.http.dto.user import UserResponse


def create_router(
    handler: AuthHandler,
    feature_service: FeatureHTTPPort,
    log: GenericLoggingPort,
) -> APIRouter:
    logdep = logger(log)
    guard_manage = feature_guard("auth:manage", feature_service)

    router = APIRouter(prefix="/auth")

    @router.post("/sign-up", response_model=TokenResponse, dependencies=[logdep])
    async def sign_up(request: SignUpRequest) -> TokenResponse:
        return await handler.post_sign_up(request)

    @router.post("/sign-in", response_model=TokenResponse, dependencies=[logdep])
    async def sign_in(request: SignInRequest) -> TokenResponse:
        return await handler.post_sign_in(request)

    @router.post("/refresh-token", response_model=TokenResponse, dependencies=[logdep])
    async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
        return await handler.post_refresh_token(request)

    @router.post("/sign-out", dependencies=[logdep])
    async def sign_out():
        return await handler.post_sign_out()

    @router.post("/register", response_model=UserResponse, dependencies=[logdep, guard_manage])
    async def register(request: RegisterRequest) -> UserResponse:
        return await handler.post_register(request)

    @router.patch("/me/password", dependencies=[logdep])
    async def patch_auth_me_password(data: SetNewPasswordWithOldPasswordRequest):
        return await handler.patch_auth_me_password(data)

    @router.patch("/me/info", dependencies=[logdep])
    async def patch_auth_me_info(request: SetAuthInfoRequest):
        return await handler.patch_auth_me_info(request)

    @router.patch("/{user_id}/password", dependencies=[logdep, guard_manage])
    async def patch_new_password(user_id: str, request: SetNewPasswordRequest):
        return await handler.patch_new_password(user_id, request)

    @router.patch("/{user_id}/info", dependencies=[logdep, guard_manage])
    async def patch_auth_info(user_id: str, request: SetAuthInfoRequest):
        return await handler.patch_auth_info(user_id, request)

    return router
