from typing import Optional
from fastapi import Request, Response, status
from ips_app.ports.driving.http.permission import PermissionHTTPPort
from ips_app.adapters.driving.http.dto.permission import (
    AddPermissionRequest,
    SetPermissionRequest,
    PermissionResponse,
    PermissionsResponse
)

class PermissionHandler:
    def __init__(self, service: PermissionHTTPPort):
        self.service = service

    async def post_permission(self, request: AddPermissionRequest) -> PermissionResponse:
        request.validate_fields()
        permission = await self.service.add_permission(
            name=request.name,
            description=request.description
        )
        return PermissionResponse.from_domain(permission)

    async def get_permission(self, permission_id: str) -> PermissionResponse:
        permission = await self.service.get_permission(permission_id)
        return PermissionResponse.from_domain(permission)

    async def get_permissions(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> PermissionsResponse:
        items, total = await self.service.get_permissions(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search
        )
        return PermissionsResponse.from_domain(
            items=items,
            page=page,
            limit=limit,
            total=total
        )

    async def patch_permission(
        self,
        permission_id: str,
        request: SetPermissionRequest
    ) -> PermissionResponse:
        request.validate_fields()
        permission = await self.service.set_permission(
            permission_id=permission_id,
            name=request.name,
            description=request.description
        )
        return PermissionResponse.from_domain(permission)

    async def patch_permission_preferences(
        self,
        permission_id: str,
        request: Request
    ) -> PermissionResponse:
        body = await request.body()
        permission = await self.service.set_permission_preferences(
            permission_id=permission_id,
            preferences=body
        )
        return PermissionResponse.from_domain(permission)

    async def delete_permission(self, permission_id: str) -> Response:
        message = await self.service.remove_permission(permission_id)
        return Response(content=message, status_code=status.HTTP_200_OK)
