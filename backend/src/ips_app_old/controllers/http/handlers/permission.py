from typing import Optional, Union

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from ips_app_old.controllers.http.dto.permission import (
    AddPermissionRequest,
    PermissionResponse,
    PermissionsResponse,
    SetPermissionRequest,
)
from ips_app_old.controllers.http.handlers.exception import handle_exception
from ips_app_old.domain.ports.driving.http.permission import PermissionHTTP


class PermissionHandler:
    def __init__(self, service: PermissionHTTP):
        self.service = service

    def _handle_exception(self, error: Exception) -> JSONResponse:
        return handle_exception(error)

    async def post_permission(
        self,
        request: AddPermissionRequest,
    ) -> Union[PermissionResponse, JSONResponse]:
        try:
            request.validate_fields()
            permission = await self.service.add_permission(
                name=request.name,
                description=request.description,
            )
            return PermissionResponse.from_domain(permission)
        except Exception as e:
            return self._handle_exception(e)

    async def get_permission(
        self,
        permission_id: str,
    ) -> Union[PermissionResponse, JSONResponse]:
        try:
            permission = await self.service.get_permission(permission_id)
            return PermissionResponse.from_domain(permission)
        except Exception as e:
            return self._handle_exception(e)

    async def get_permissions(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Union[PermissionsResponse, JSONResponse]:
        try:
            items, total = await self.service.get_permissions(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
            )
            return PermissionsResponse.from_domain(
                items=items,
                page=page,
                limit=limit,
                total=total,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def patch_permission(
        self,
        permission_id: str,
        request: SetPermissionRequest,
    ) -> Union[PermissionResponse, JSONResponse]:
        try:
            request.validate_fields()
            permission = await self.service.set_permission(
                permission_id=permission_id,
                name=request.name,
                description=request.description,
            )
            return PermissionResponse.from_domain(permission)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_permission_preferences(
        self,
        permission_id: str,
        request: Request,
    ) -> Union[PermissionResponse, JSONResponse]:
        try:
            body = await request.body()
            permission = await self.service.set_permission_preferences(
                permission_id=permission_id,
                preferences=body,
            )
            return PermissionResponse.from_domain(permission)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_permission(
        self,
        permission_id: str,
    ) -> Union[Response, JSONResponse]:
        try:
            message = await self.service.remove_permission(permission_id)
            return Response(content=message, status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)
