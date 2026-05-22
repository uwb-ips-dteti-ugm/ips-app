from typing import List, Optional, Union

from fastapi import HTTPException, Request, status as http_status
from fastapi.responses import JSONResponse

from ips_app.controllers.http.dto.common import ErrorResponse, MessageResponse
from ips_app.controllers.http.dto.permission import PermissionResponse
from ips_app.controllers.http.dto.user import (
    SetUserInfoRequest,
    SetUserRoleRequest,
    SetUserStatusRequest,
    UserResponse,
    UsersResponse,
)
from ips_app.controllers.http.middlewares.auth_jwt import get_claims
from ips_app.domain.models.exception import (
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.user import UserStatus
from ips_app.domain.ports.driving.http.user import UserHTTP


class UserHandler:
    def __init__(self, service: UserHTTP):
        self.service = service

    async def get_user(self, user_id: str) -> Union[UserResponse, JSONResponse]:
        try:
            user = await self.service.get_user(user_id)
            return UserResponse.from_domain(user)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error="User not found.").model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading the user. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading the user. Please try again."
                ).model_dump(),
            )

    async def get_user_me(self) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                return JSONResponse(
                    status_code=http_status.HTTP_401_UNAUTHORIZED,
                    content=ErrorResponse(
                        error="Please sign in to continue."
                    ).model_dump(),
                )
            user = await self.service.get_user(claims.user_id)
            return UserResponse.from_domain(user)
        except Exception as e:
            if isinstance(e, HTTPException):
                return JSONResponse(
                    status_code=e.status_code,
                    content=ErrorResponse(
                        error="Please sign in to continue."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="Your account could not be found. Please sign in again."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading your account. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading your account. Please try again."
                ).model_dump(),
            )

    async def get_users(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
        role_id: Optional[str] = None,
        status: Optional[UserStatus] = None,
    ) -> Union[UsersResponse, JSONResponse]:
        try:
            items, total = await self.service.get_users(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
                role_id=role_id,
                status=status,
            )
            return UsersResponse.from_domain(
                items=items,
                page=page,
                limit=limit,
                total=total,
            )
        except Exception as e:
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading users. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading users. Please try again."
                ).model_dump(),
            )

    async def get_user_permissions(
        self,
        user_id: str,
    ) -> Union[List[PermissionResponse], JSONResponse]:
        try:
            permissions = await self.service.get_user_permissions(user_id)
            return [
                PermissionResponse.from_domain(permission)
                for permission in permissions
            ]
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                if e.group_name == "roles":
                    error = "The user's role could not be found."
                else:
                    error = "The selected user does not exist."
                return JSONResponse(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading user permissions. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading user permissions. Please try again."
                ).model_dump(),
            )

    async def get_user_me_permissions(
        self,
    ) -> Union[List[PermissionResponse], JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                return JSONResponse(
                    status_code=http_status.HTTP_401_UNAUTHORIZED,
                    content=ErrorResponse(
                        error="Please sign in to continue."
                    ).model_dump(),
                )
            permissions = await self.service.get_user_permissions(claims.user_id)
            return [
                PermissionResponse.from_domain(permission)
                for permission in permissions
            ]
        except Exception as e:
            if isinstance(e, HTTPException):
                return JSONResponse(
                    status_code=e.status_code,
                    content=ErrorResponse(
                        error="Please sign in to continue."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                if e.group_name == "roles":
                    error = "Your role could not be found. Please contact an administrator."
                else:
                    error = "Your account could not be found. Please sign in again."
                return JSONResponse(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading your permissions. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading your permissions. Please try again."
                ).model_dump(),
            )

    async def patch_user_info(
        self,
        user_id: str,
        request: SetUserInfoRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            user = await self.service.set_user_info(
                user_id=user_id,
                name=request.name,
                bio=request.bio,
                updated_by=claims.user_id if claims else None,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The user you want to update does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating the user. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating the user. Please try again."
                ).model_dump(),
            )

    async def patch_user_me_info(
        self,
        request: SetUserInfoRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                return JSONResponse(
                    status_code=http_status.HTTP_401_UNAUTHORIZED,
                    content=ErrorResponse(
                        error="Please sign in to continue."
                    ).model_dump(),
                )
            request.validate_fields()
            user = await self.service.set_user_info(
                user_id=claims.user_id,
                name=request.name,
                bio=request.bio,
                updated_by=claims.user_id,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            if isinstance(e, HTTPException):
                return JSONResponse(
                    status_code=e.status_code,
                    content=ErrorResponse(
                        error="Please sign in to continue."
                    ).model_dump(),
                )
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="Your account could not be found. Please sign in again."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating your profile. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating your profile. Please try again."
                ).model_dump(),
            )

    async def patch_user_preferences(
        self,
        user_id: str,
        request: Request,
    ) -> Union[UserResponse, JSONResponse]:
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
            user = await self.service.set_user_preferences(
                user_id=user_id,
                preferences=preferences,
                updated_by=claims.user_id if claims else None,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The user preferences could not be updated because the user does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating user preferences. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating user preferences. Please try again."
                ).model_dump(),
            )

    async def patch_user_me_preferences(
        self,
        request: Request,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                return JSONResponse(
                    status_code=http_status.HTTP_401_UNAUTHORIZED,
                    content=ErrorResponse(
                        error="Please sign in to continue."
                    ).model_dump(),
                )
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
            user = await self.service.set_user_preferences(
                user_id=claims.user_id,
                preferences=preferences,
                updated_by=claims.user_id,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            if isinstance(e, HTTPException):
                return JSONResponse(
                    status_code=e.status_code,
                    content=ErrorResponse(
                        error="Please sign in to continue."
                    ).model_dump(),
                )
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="Your account could not be found. Please sign in again."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating your preferences. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating your preferences. Please try again."
                ).model_dump(),
            )

    async def patch_user_role(
        self,
        user_id: str,
        request: SetUserRoleRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            user = await self.service.set_user_role(
                user_id=user_id,
                role_id=request.role_id,
                updated_by=claims.user_id if claims else None,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, DuplicateDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_409_CONFLICT,
                    content=ErrorResponse(
                        error="A user with this information already exists."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                if e.group_name == "roles":
                    error = "The selected role does not exist. Please choose another role."
                else:
                    error = "The user role could not be updated because the user does not exist."
                return JSONResponse(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error="You do not have permission to change this user's role."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating the user role. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating the user role. Please try again."
                ).model_dump(),
            )

    async def patch_user_status(
        self,
        user_id: str,
        request: SetUserStatusRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            user = await self.service.set_user_status(
                user_id=user_id,
                status=request.status,
                updated_by=claims.user_id if claims else None,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The user status could not be updated because the user does not exist."
                    ).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error="You do not have permission to change this user's http_status."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating the user http_status. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating the user http_status. Please try again."
                ).model_dump(),
            )

    async def delete_user(self, user_id: str) -> Union[MessageResponse, JSONResponse]:
        try:
            message = await self.service.remove_user(user_id)
            return MessageResponse(message=message)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The user you want to delete does not exist."
                    ).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error="You do not have permission to delete this user."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while deleting the user. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while deleting the user. Please try again."
                ).model_dump(),
            )
