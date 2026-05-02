from typing import Optional
from fastapi import APIRouter, Request
from ips_app.adapters.driving.http.handler.permission import PermissionHandler
from ips_app.adapters.driving.http.dto.permission import (
    AddPermissionRequest,
    SetPermissionRequest,
    PermissionResponse,
    PermissionsResponse,
)

def create_router(handler: PermissionHandler) -> APIRouter:
    router = APIRouter(prefix="/permissions")

    @router.post("", response_model=PermissionResponse)
    async def post_permission(request: AddPermissionRequest) -> PermissionResponse:
        return await handler.post_permission(request)

    @router.get("", response_model=PermissionsResponse)
    async def get_permissions(
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> PermissionsResponse:
        return await handler.get_permissions(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search,
        )

    @router.get("/{permission_id}", response_model=PermissionResponse)
    async def get_permission(permission_id: str) -> PermissionResponse:
        return await handler.get_permission(permission_id)

    @router.patch("/{permission_id}", response_model=PermissionResponse)
    async def patch_permission(permission_id: str, request: SetPermissionRequest) -> PermissionResponse:
        return await handler.patch_permission(permission_id, request)

    @router.patch("/{permission_id}/preferences", response_model=PermissionResponse)
    async def patch_permission_preferences(permission_id: str, request: Request) -> PermissionResponse:
        return await handler.patch_permission_preferences(permission_id, request)

    @router.delete("/{permission_id}")
    async def delete_permission(permission_id: str):
        return await handler.delete_permission(permission_id)

    return router
