from typing import Optional
from fastapi import APIRouter, Request
from ips_app.adapters.driving.http.handler.user import UserHandler
from ips_app.adapters.driving.http.dto.user import (
    SetUserInfoRequest,
    SetUserRoleRequest,
    SetUserStateRequest,
    SetUserStatusRequest,
    UserResponse,
    UsersResponse,
)

def create_router(handler: UserHandler) -> APIRouter:
    router = APIRouter(prefix="/users")

    @router.get("/me", response_model=UserResponse)
    async def get_user_me() -> UserResponse:
        return await handler.get_user_me()

    @router.patch("/me/info", response_model=UserResponse)
    async def patch_user_me_info(request: SetUserInfoRequest) -> UserResponse:
        return await handler.patch_user_me_info(request)

    @router.patch("/me/preferences", response_model=UserResponse)
    async def patch_user_me_preferences(request: Request) -> UserResponse:
        return await handler.patch_user_me_preferences(request)

    @router.patch("/me/state", response_model=UserResponse)
    async def patch_user_me_state(request: SetUserStateRequest) -> UserResponse:
        return await handler.patch_user_me_state(request)

    @router.get("", response_model=UsersResponse)
    async def get_users(
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
        role_id: Optional[str] = None,
    ) -> UsersResponse:
        return await handler.get_users(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search,
            role_id=role_id,
        )

    @router.get("/{user_id}", response_model=UserResponse)
    async def get_user(user_id: str) -> UserResponse:
        return await handler.get_user(user_id)

    @router.patch("/{user_id}/info", response_model=UserResponse)
    async def patch_user_info(user_id: str, request: SetUserInfoRequest) -> UserResponse:
        return await handler.patch_user_info(user_id, request)

    @router.patch("/{user_id}/preferences", response_model=UserResponse)
    async def patch_user_preferences(user_id: str, request: Request) -> UserResponse:
        return await handler.patch_user_preferences(user_id, request)

    @router.patch("/{user_id}/role", response_model=UserResponse)
    async def patch_user_role(user_id: str, request: SetUserRoleRequest) -> UserResponse:
        return await handler.patch_user_role(user_id, request)

    @router.patch("/{user_id}/state", response_model=UserResponse)
    async def patch_user_state(user_id: str, request: SetUserStateRequest) -> UserResponse:
        return await handler.patch_user_state(user_id, request)

    @router.patch("/{user_id}/status", response_model=UserResponse)
    async def patch_user_status(user_id: str, request: SetUserStatusRequest) -> UserResponse:
        return await handler.patch_user_status(user_id, request)

    @router.delete("/{user_id}")
    async def delete_user(user_id: str):
        return await handler.delete_user(user_id)

    return router
