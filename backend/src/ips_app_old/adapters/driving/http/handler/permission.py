from typing import Optional, Union
from fastapi import Request, Response, status, HTTPException
from fastapi.responses import JSONResponse
from ips_app_old.ports.driving.http.permission import PermissionHTTPPort
from ips_app_old.domain.models.exception import (
    NotFoundException,
    DuplicateException,
    ValidatorException,
)
from ips_app_old.adapters.driving.http.dto.permission import (
    AddPermissionRequest,
    SetPermissionRequest,
    PermissionResponse,
    PermissionsResponse
)
from ips_app_old.adapters.driving.http.dto.common import ErrorResponse

class PermissionHandler:
    def __init__(self, service: PermissionHTTPPort):
        self.service = service

    def _handle_exception(self, e: Exception) -> JSONResponse:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = "Internal server error"

        if isinstance(e, ValidatorException):
            status_code = status.HTTP_400_BAD_REQUEST
            message = str(e)
        elif isinstance(e, NotFoundException):
            status_code = status.HTTP_404_NOT_FOUND
            message = f"Resource '{e.data_name}' in '{e.group_name}' not found"
        elif isinstance(e, DuplicateException):
            status_code = status.HTTP_409_CONFLICT
            message = f"Resource '{e.data_name}' in '{e.group_name}' already exists"
        elif isinstance(e, HTTPException):
            status_code = e.status_code
            message = str(e.detail)
        
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(error=message).model_dump()
        )

    async def post_permission(self, request: AddPermissionRequest) -> Union[PermissionResponse, JSONResponse]:
        try:
            request.validate_fields()
            permission = await self.service.add_permission(
                name=request.name,
                description=request.description
            )
            return PermissionResponse.from_domain(permission)
        except Exception as e:
            return self._handle_exception(e)

    async def get_permission(self, permission_id: str) -> Union[PermissionResponse, JSONResponse]:
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
        search: Optional[str] = None
    ) -> Union[PermissionsResponse, JSONResponse]:
        try:
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
        except Exception as e:
            return self._handle_exception(e)

    async def patch_permission(
        self,
        permission_id: str,
        request: SetPermissionRequest
    ) -> Union[PermissionResponse, JSONResponse]:
        try:
            request.validate_fields()
            permission = await self.service.set_permission(
                permission_id=permission_id,
                name=request.name,
                description=request.description
            )
            return PermissionResponse.from_domain(permission)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_permission_preferences(
        self,
        permission_id: str,
        request: Request
    ) -> Union[PermissionResponse, JSONResponse]:
        try:
            body = await request.body()
            permission = await self.service.set_permission_preferences(
                permission_id=permission_id,
                preferences=body
            )
            return PermissionResponse.from_domain(permission)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_permission(self, permission_id: str) -> Union[Response, JSONResponse]:
        try:
            message = await self.service.remove_permission(permission_id)
            return Response(content=message, status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)
