from typing import Optional, List
from fastapi import Request, Response, status
from ips_app.ports.driving.http.role import RoleHTTPPort
from ips_app.adapters.driving.http.dto.role import (
    AddRoleRequest,
    SetRoleRequest,
    RoleResponse,
    RolesResponse
)
from ips_app.adapters.driving.http.dto.permission import PermissionResponse
from ips_app.adapters.driving.http.dto.common import PermissionIdsRequest

class RoleHandler:
    def __init__(self, service: RoleHTTPPort):
        self.service = service

    async def post_role(self, request: AddRoleRequest) -> RoleResponse:
        request.validate_fields()
        role = await self.service.add_role(
            name=request.name,
            description=request.description
        )
        return RoleResponse.from_domain(role)

    async def get_role(self, role_id: str) -> RoleResponse:
        role = await self.service.get_role(role_id)
        return RoleResponse.from_domain(role)

    async def get_roles(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> RolesResponse:
        items, total = await self.service.get_roles(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search
        )
        return RolesResponse.from_domain(
            items=items,
            page=page,
            limit=limit,
            total=total
        )

    async def patch_role(
        self,
        role_id: str,
        request: SetRoleRequest
    ) -> RoleResponse:
        request.validate_fields()
        role = await self.service.set_role(
            role_id=role_id,
            name=request.name,
            description=request.description
        )
        return RoleResponse.from_domain(role)

    async def patch_role_preferences(
        self,
        role_id: str,
        request: Request
    ) -> RoleResponse:
        body = await request.body()
        role = await self.service.set_role_preferences(
            role_id=role_id,
            preferences=body
        )
        return RoleResponse.from_domain(role)

    async def delete_role(self, role_id: str) -> Response:
        message = await self.service.remove_role(role_id)
        return Response(content=message, status_code=status.HTTP_200_OK)

    async def post_role_permissions(
        self,
        role_id: str,
        request: PermissionIdsRequest
    ) -> RoleResponse:
        request.validate_fields()
        role = await self.service.add_permissions_to_role(
            role_id=role_id,
            permission_ids=request.permission_ids
        )
        return RoleResponse.from_domain(role)

    async def delete_role_permissions(
        self,
        role_id: str,
        request: PermissionIdsRequest
    ) -> RoleResponse:
        request.validate_fields()
        role = await self.service.remove_permissions_from_role(
            role_id=role_id,
            permission_ids=request.permission_ids
        )
        return RoleResponse.from_domain(role)

    async def get_role_permissions(self, role_id: str) -> List[PermissionResponse]:
        permissions = await self.service.get_role_permissions(role_id)
        return [PermissionResponse.from_domain(p) for p in permissions]
