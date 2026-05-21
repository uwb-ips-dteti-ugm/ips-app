from fastapi import APIRouter

from ips_app_old.controllers.http.dto.auth import (
    RefreshTokenRequest,
    RegisterRequest,
    SetAuthInfoRequest,
    SetNewPasswordRequest,
    SetNewPasswordWithOldPasswordRequest,
    SignInRequest,
    SignUpRequest,
    TokenResponse,
)
from ips_app_old.controllers.http.dto.common import ErrorResponse
from ips_app_old.controllers.http.dto.user import UserResponse
from ips_app_old.controllers.http.handlers.auth import AuthHandler
from ips_app_old.controllers.http.middlewares.feature_guard import feature_guard
from ips_app_old.controllers.http.middlewares.logger import logger
from ips_app_old.domain.ports.driven.logging.generic import GenericLogging
from ips_app_old.domain.ports.driving.http.user import UserHTTP


def create_router(
    handler: AuthHandler,
    user_service: UserHTTP,
    log: GenericLogging,
) -> APIRouter:
    guard_manage = feature_guard("auth/manage", user_service)

    router = APIRouter(
        prefix="/auth",
        tags=["Auth"],
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
        "/sign-up",
        response_model=TokenResponse,
        dependencies=[
            logger(
                log,
                tag="AuthRoutes.sign_up",
                msg_2xx="User signed up successfully",
                msg_4xx="User sign-up rejected",
                msg_5xx="User sign-up failed",
            )
        ],
    )
    async def sign_up(request: SignUpRequest):
        return await handler.post_sign_up(request)

    @router.post(
        "/sign-in",
        response_model=TokenResponse,
        dependencies=[
            logger(
                log,
                tag="AuthRoutes.sign_in",
                msg_2xx="User signed in successfully",
                msg_4xx="User sign-in rejected",
                msg_5xx="User sign-in failed",
            )
        ],
    )
    async def sign_in(request: SignInRequest):
        return await handler.post_sign_in(request)

    @router.post(
        "/refresh-token",
        response_model=TokenResponse,
        dependencies=[
            logger(
                log,
                tag="AuthRoutes.refresh_token",
                msg_2xx="Auth token refreshed successfully",
                msg_4xx="Auth token refresh rejected",
                msg_5xx="Auth token refresh failed",
            )
        ],
    )
    async def refresh_token(request: RefreshTokenRequest):
        return await handler.post_refresh_token(request)

    @router.post(
        "/sign-out",
        dependencies=[
            logger(
                log,
                tag="AuthRoutes.sign_out",
                msg_2xx="User signed out successfully",
                msg_4xx="User sign-out rejected",
                msg_5xx="User sign-out failed",
            )
        ],
    )
    async def sign_out():
        return await handler.post_sign_out()

    @router.post(
        "/register",
        response_model=UserResponse,
        dependencies=[
            logger(
                log,
                tag="AuthRoutes.register",
                msg_2xx="User registered successfully",
                msg_4xx="User registration rejected",
                msg_5xx="User registration failed",
            ),
            guard_manage,
        ],
    )
    async def register(request: RegisterRequest):
        return await handler.post_register(request)

    @router.patch(
        "/me/password",
        dependencies=[
            logger(
                log,
                tag="AuthRoutes.patch_me_password",
                msg_2xx="Current user password updated successfully",
                msg_4xx="Current user password update rejected",
                msg_5xx="Current user password update failed",
            )
        ],
    )
    async def patch_auth_me_password(request: SetNewPasswordWithOldPasswordRequest):
        return await handler.patch_auth_me_password(request)

    @router.patch(
        "/me/info",
        dependencies=[
            logger(
                log,
                tag="AuthRoutes.patch_me_info",
                msg_2xx="Current user auth info updated successfully",
                msg_4xx="Current user auth info update rejected",
                msg_5xx="Current user auth info update failed",
            )
        ],
    )
    async def patch_auth_me_info(request: SetAuthInfoRequest):
        return await handler.patch_auth_me_info(request)

    @router.patch(
        "/{user_id}/password",
        dependencies=[
            logger(
                log,
                tag="AuthRoutes.patch_user_password",
                msg_2xx="User password set successfully",
                msg_4xx="User password set rejected",
                msg_5xx="User password set failed",
            ),
            guard_manage,
        ],
    )
    async def patch_new_password(user_id: str, request: SetNewPasswordRequest):
        return await handler.patch_new_password(user_id, request)

    @router.patch(
        "/{user_id}/info",
        dependencies=[
            logger(
                log,
                tag="AuthRoutes.patch_user_info",
                msg_2xx="User auth info updated successfully",
                msg_4xx="User auth info update rejected",
                msg_5xx="User auth info update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_auth_info(user_id: str, request: SetAuthInfoRequest):
        return await handler.patch_auth_info(user_id, request)

    return router
