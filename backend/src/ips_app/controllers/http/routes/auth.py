from fastapi import APIRouter

from ips_app.controllers.http.dto.auth import (
    RefreshTokenRequest,
    RegisterRequest,
    SetPasswordAuthInfoRequest,
    SetPasswordAuthRequest,
    SetPasswordWithOldPasswordRequest,
    SignInRequest,
    TokenResponse,
)
from ips_app.controllers.http.dto.common import ErrorResponse
from ips_app.controllers.http.dto.user import UserResponse
from ips_app.controllers.http.handlers.auth import AuthHandler
from ips_app.controllers.http.middlewares.logger import logger
from ips_app.controllers.http.middlewares.permission_check import permission_check
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driving.http.role import RoleHTTP


def create_router(
    handler: AuthHandler,
    role_service: RoleHTTP,
    log: LeveledLogging,
) -> APIRouter:
    guard_manage = permission_check(["auth/manage"], role_service)

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
    async def patch_auth_me_password(request: SetPasswordWithOldPasswordRequest):
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
    async def patch_auth_me_info(request: SetPasswordAuthInfoRequest):
        return await handler.patch_auth_me_info(request)

    @router.patch(
        "/{user_id}/password-auth",
        dependencies=[
            logger(
                log,
                tag="AuthRoutes.patch_user_password_auth",
                msg_2xx="User password auth updated successfully",
                msg_4xx="User password auth update rejected",
                msg_5xx="User password auth update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_user_password_auth(
        user_id: str,
        request: SetPasswordAuthRequest,
    ):
        return await handler.patch_user_password_auth(user_id, request)

    return router
