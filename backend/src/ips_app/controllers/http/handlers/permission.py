from typing import Optional, Union

from fastapi import Request, status
from fastapi.responses import JSONResponse

from ips_app.controllers.http.dto.common import ErrorResponse, MessageResponse
from ips_app.controllers.http.dto.permission import (
    AddPermissionRequest,
    PermissionResponse,
    PermissionsResponse,
    SetPermissionRequest,
)
from ips_app.controllers.http.middlewares.auth_jwt import get_claims
from ips_app.domain.models.exception import (
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.ports.driving.http.permission import PermissionHTTP


class PermissionHandler:
    def __init__(self, service: PermissionHTTP):
        self.service = service

    async def post_permission(
        self,
        request: AddPermissionRequest,
    ) -> Union[PermissionResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            permission = await self.service.add_permission(
                name=request.name,
                description=request.description,
                created_by=claims.user_id if claims else None,
            )
            return PermissionResponse.from_domain(permission)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, DuplicateDomainException):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content=ErrorResponse(
                        error="A permission with this name already exists. Please choose another name."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while creating the permission. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while creating the permission. Please try again."
                ).model_dump(),
            )

    async def get_permission(
        self,
        permission_id: str,
    ) -> Union[PermissionResponse, JSONResponse]:
        try:
            permission = await self.service.get_permission(permission_id)
            return PermissionResponse.from_domain(permission)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error="Permission not found.").model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading the permission. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading the permission. Please try again."
                ).model_dump(),
            )

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
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading permissions. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading permissions. Please try again."
                ).model_dump(),
            )

    async def patch_permission(
        self,
        permission_id: str,
        request: SetPermissionRequest,
    ) -> Union[PermissionResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            permission = await self.service.set_permission(
                permission_id=permission_id,
                name=request.name,
                description=request.description,
                updated_by=claims.user_id if claims else None,
            )
            return PermissionResponse.from_domain(permission)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, DuplicateDomainException):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content=ErrorResponse(
                        error="A permission with this name already exists. Please choose another name."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The permission you want to update does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating the permission. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating the permission. Please try again."
                ).model_dump(),
            )

    async def patch_permission_preferences(
        self,
        permission_id: str,
        request: Request,
    ) -> Union[PermissionResponse, JSONResponse]:
        try:
            claims = get_claims()
            try:
                preferences = await request.json()
            except Exception as error:
                raise ValidatorDomainException(
                    "Preferences must be valid JSON."
                ) from error
            if not isinstance(preferences, dict):
                raise ValidatorDomainException(
                    "Preferences must be a JSON object."
                )
            permission = await self.service.set_permission_preferences(
                permission_id=permission_id,
                preferences=preferences,
                updated_by=claims.user_id if claims else None,
            )
            return PermissionResponse.from_domain(permission)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The permission preferences could not be updated because the permission does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating permission preferences. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating permission preferences. Please try again."
                ).model_dump(),
            )

    async def delete_permission(
        self,
        permission_id: str,
    ) -> Union[MessageResponse, JSONResponse]:
        try:
            message = await self.service.remove_permission(permission_id)
            return MessageResponse(message=message)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The permission you want to delete does not exist."
                    ).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error="This permission cannot be deleted because one or more roles still use it."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while deleting the permission. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while deleting the permission. Please try again."
                ).model_dump(),
            )
