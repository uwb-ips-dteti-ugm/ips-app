from typing import List, Optional, Union

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from ips_app_old.controllers.http.dto.common import PermissionIdsRequest
from ips_app_old.controllers.http.dto.permission import PermissionResponse
from ips_app_old.controllers.http.dto.role import (
    AddRoleRequest,
    RoleResponse,
    RolesResponse,
    SetRoleRequest,
)
from ips_app_old.controllers.http.handlers.exception import handle_exception
from ips_app_old.domain.ports.driving.http.role import RoleHTTP


class RoleHandler:
    def __init__(self, service: RoleHTTP):
        self.service = service

    def _handle_exception(self, error: Exception) -> JSONResponse:
        return handle_exception(error)

    async def post_role(
        self,
        request: AddRoleRequest,
    ) -> Union[RoleResponse, JSONResponse]:
        try:
            request.validate_fields()
            role = await self.service.add_role(
                name=request.name,
                description=request.description,
            )
            return RoleResponse.from_domain(role)
        except Exception as e:
            return self._handle_exception(e)

    async def get_role(self, role_id: str) -> Union[RoleResponse, JSONResponse]:
        try:
            role = await self.service.get_role(role_id)
            return RoleResponse.from_domain(role)
        except Exception as e:
            return self._handle_exception(e)

    async def get_roles(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Union[RolesResponse, JSONResponse]:
        try:
            items, total = await self.service.get_roles(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
            )
            return RolesResponse.from_domain(
                items=items,
                page=page,
                limit=limit,
                total=total,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def patch_role(
        self,
        role_id: str,
        request: SetRoleRequest,
    ) -> Union[RoleResponse, JSONResponse]:
        try:
            request.validate_fields()
            role = await self.service.set_role(
                role_id=role_id,
                name=request.name,
                description=request.description,
            )
            return RoleResponse.from_domain(role)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_role_preferences(
        self,
        role_id: str,
        request: Request,
    ) -> Union[RoleResponse, JSONResponse]:
        try:
            body = await request.body()
            role = await self.service.set_role_preferences(
                role_id=role_id,
                preferences=body,
            )
            return RoleResponse.from_domain(role)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_role(self, role_id: str) -> Union[Response, JSONResponse]:
        try:
            message = await self.service.remove_role(role_id)
            return Response(content=message, status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)

    async def post_role_permissions(
        self,
        role_id: str,
        request: PermissionIdsRequest,
    ) -> Union[RoleResponse, JSONResponse]:
        try:
            request.validate_fields()
            role = await self.service.add_permissions_to_role(
                role_id=role_id,
                permission_ids=request.permission_ids,
            )
            return RoleResponse.from_domain(role)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_role_permissions(
        self,
        role_id: str,
        request: PermissionIdsRequest,
    ) -> Union[RoleResponse, JSONResponse]:
        try:
            request.validate_fields()
            role = await self.service.remove_permissions_from_role(
                role_id=role_id,
                permission_ids=request.permission_ids,
            )
            return RoleResponse.from_domain(role)
        except Exception as e:
            return self._handle_exception(e)

    async def get_role_permissions(
        self,
        role_id: str,
    ) -> Union[List[PermissionResponse], JSONResponse]:
        try:
            permissions = await self.service.get_role_permissions(role_id)
            return [
                PermissionResponse.from_domain(permission)
                for permission in permissions
            ]
        except Exception as e:
            return self._handle_exception(e)
