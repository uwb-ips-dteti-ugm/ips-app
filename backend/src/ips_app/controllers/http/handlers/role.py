from typing import List, Optional, Union

from fastapi import Request, status
from fastapi.responses import JSONResponse

from ips_app.controllers.http.dto.common import (
    ErrorResponse,
    MessageResponse,
    PermissionIdsRequest,
)
from ips_app.controllers.http.dto.permission import PermissionResponse
from ips_app.controllers.http.dto.role import (
    AddRoleRequest,
    RoleResponse,
    RolesResponse,
    SetRoleRequest,
)
from ips_app.controllers.http.middlewares.auth_jwt import get_claims
from ips_app.domain.models.exception import (
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.ports.driving.http.role import RoleHTTP


class RoleHandler:
    def __init__(self, service: RoleHTTP):
        self.service = service

    async def post_role(
        self,
        request: AddRoleRequest,
    ) -> Union[RoleResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            role = await self.service.add_role(
                name=request.name,
                description=request.description,
                is_default=request.is_default,
                created_by=claims.user_id if claims else None,
            )
            return RoleResponse.from_domain(role)
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
                        error="A role with this name already exists. Please choose another name."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while creating the role. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while creating the role. Please try again."
                ).model_dump(),
            )

    async def get_role(self, role_id: str) -> Union[RoleResponse, JSONResponse]:
        try:
            role = await self.service.get_role(role_id)
            return RoleResponse.from_domain(role)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error="Role not found.").model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading the role. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading the role. Please try again."
                ).model_dump(),
            )

    async def get_default_role(self) -> Union[RoleResponse, JSONResponse]:
        try:
            role = await self.service.get_default_role()
            return RoleResponse.from_domain(role)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="No default role has been configured yet."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading the default role. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading the default role. Please try again."
                ).model_dump(),
            )

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
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading roles. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading roles. Please try again."
                ).model_dump(),
            )

    async def patch_role(
        self,
        role_id: str,
        request: SetRoleRequest,
    ) -> Union[RoleResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            role = await self.service.set_role(
                role_id=role_id,
                name=request.name,
                description=request.description,
                updated_by=claims.user_id if claims else None,
            )
            return RoleResponse.from_domain(role)
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
                        error="A role with this name already exists. Please choose another name."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The role you want to update does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating the role. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating the role. Please try again."
                ).model_dump(),
            )

    async def patch_default_role(
        self,
        role_id: str,
    ) -> Union[RoleResponse, JSONResponse]:
        try:
            claims = get_claims()
            role = await self.service.set_default_role(
                role_id=role_id,
                updated_by=claims.user_id if claims else None,
            )
            return RoleResponse.from_domain(role)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The role you want to set as default does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while setting the default role. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while setting the default role. Please try again."
                ).model_dump(),
            )

    async def patch_role_preferences(
        self,
        role_id: str,
        request: Request,
    ) -> Union[RoleResponse, JSONResponse]:
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
            role = await self.service.set_role_preferences(
                role_id=role_id,
                preferences=preferences,
                updated_by=claims.user_id if claims else None,
            )
            return RoleResponse.from_domain(role)
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
                        error="The role preferences could not be updated because the role does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating role preferences. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating role preferences. Please try again."
                ).model_dump(),
            )

    async def delete_role(self, role_id: str) -> Union[MessageResponse, JSONResponse]:
        try:
            message = await self.service.remove_role(role_id)
            return MessageResponse(message=message)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The role you want to delete does not exist."
                    ).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error="This role cannot be deleted because one or more users still use it."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while deleting the role. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while deleting the role. Please try again."
                ).model_dump(),
            )

    async def post_role_permissions(
        self,
        role_id: str,
        request: PermissionIdsRequest,
    ) -> Union[RoleResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            role = await self.service.add_permissions_to_role(
                role_id=role_id,
                permission_ids=request.permission_ids,
                updated_by=claims.user_id if claims else None,
            )
            return RoleResponse.from_domain(role)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                if e.group_name == "permissions":
                    error = "One or more selected permissions do not exist."
                else:
                    error = "The role you want to update does not exist."
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while adding permissions to the role. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while adding permissions to the role. Please try again."
                ).model_dump(),
            )

    async def delete_role_permissions(
        self,
        role_id: str,
        request: PermissionIdsRequest,
    ) -> Union[RoleResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            role = await self.service.remove_permissions_from_role(
                role_id=role_id,
                permission_ids=request.permission_ids,
                updated_by=claims.user_id if claims else None,
            )
            return RoleResponse.from_domain(role)
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
                        error="The role you want to update does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while removing permissions from the role. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while removing permissions from the role. Please try again."
                ).model_dump(),
            )

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
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The role permissions could not be loaded because the role does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading role permissions. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading role permissions. Please try again."
                ).model_dump(),
            )
