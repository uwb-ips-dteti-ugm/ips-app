from fastapi import APIRouter
from ips_app.adapters.driving.http.handler.auth import AuthHandler
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


def create_router(handler: AuthHandler) -> APIRouter:
    router = APIRouter(prefix="/auth")

    @router.post("/sign-up", response_model=TokenResponse)
    async def sign_up(request: SignUpRequest) -> TokenResponse:
        return await handler.post_sign_up(request)

    @router.post("/sign-in", response_model=TokenResponse)
    async def sign_in(request: SignInRequest) -> TokenResponse:
        return await handler.post_sign_in(request)

    @router.post("/refresh-token", response_model=TokenResponse)
    async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
        return await handler.post_refresh_token(request)

    @router.post("/sign-out")
    async def sign_out():
        return await handler.post_sign_out()

    @router.post("/register", response_model=UserResponse)
    async def register(request: RegisterRequest) -> UserResponse:
        return await handler.post_register(request)

    @router.patch("/me/password")
    async def patch_auth_me_password(data: SetNewPasswordWithOldPasswordRequest):
        return await handler.patch_auth_me_password(data)

    @router.patch("/me/info")
    async def patch_auth_me_info(request: SetAuthInfoRequest):
        return await handler.patch_auth_me_info(request)

    @router.patch("/{user_id}/password")
    async def patch_new_password(user_id: str, request: SetNewPasswordRequest):
        return await handler.patch_new_password(user_id, request)

    @router.patch("/{user_id}/info")
    async def patch_auth_info(user_id: str, request: SetAuthInfoRequest):
        return await handler.patch_auth_info(user_id, request)

    return router
