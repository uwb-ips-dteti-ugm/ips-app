from typing import Optional, List, Union
from fastapi import Request, Response, status, HTTPException
from fastapi.responses import JSONResponse
from ips_app.ports.driving.http.user import UserHTTPPort
from ips_app.domain.models.exception import (
    NotFoundException,
    DuplicateException,
    ValidatorException,
)
from ips_app.adapters.driving.http.dto.user import (
    SetUserInfoRequest,
    SetUserRoleRequest,
    SetUserStateRequest,
    SetUserStatusRequest,
    UserResponse,
    UsersResponse
)
from ips_app.adapters.driving.http.dto.common import ErrorResponse
from ips_app.adapters.driving.http.middleware.auth_jwt import get_claims

class UserHandler:
    def __init__(self, service: UserHTTPPort):
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

    async def get_user(self, user_id: str) -> Union[UserResponse, JSONResponse]:
        try:
            user = await self.service.get_user(user_id)
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def get_user_me(self) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(status_code=401, detail="Unauthorized")
            user = await self.service.get_user(claims.user_id)
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def get_users(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
        role_id: Optional[str] = None
    ) -> Union[UsersResponse, JSONResponse]:
        try:
            items, total = await self.service.get_users(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
                role_id=role_id
            )
            return UsersResponse.from_domain(
                items=items,
                page=page,
                limit=limit,
                total=total
            )
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_info(
        self,
        user_id: str,
        request: SetUserInfoRequest
    ) -> Union[UserResponse, JSONResponse]:
        try:
            request.validate_fields()
            user = await self.service.set_user_info(
                user_id=user_id,
                name=request.name,
                bio=request.bio
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_me_info(
        self,
        request: SetUserInfoRequest
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(status_code=401, detail="Unauthorized")
            request.validate_fields()
            user = await self.service.set_user_info(
                user_id=claims.user_id,
                name=request.name,
                bio=request.bio
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_preferences(
        self,
        user_id: str,
        request: Request
    ) -> Union[UserResponse, JSONResponse]:
        try:
            body = await request.body()
            user = await self.service.set_user_preferences(
                user_id=user_id,
                preferences=body
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_me_preferences(
        self,
        request: Request
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(status_code=401, detail="Unauthorized")
            body = await request.body()
            user = await self.service.set_user_preferences(
                user_id=claims.user_id,
                preferences=body
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_role(
        self,
        user_id: str,
        request: SetUserRoleRequest
    ) -> Union[UserResponse, JSONResponse]:
        try:
            request.validate_fields()
            user = await self.service.set_user_role(
                user_id=user_id,
                role_id=request.role_id
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_state(
        self,
        user_id: str,
        request: SetUserStateRequest
    ) -> Union[UserResponse, JSONResponse]:
        try:
            user = await self.service.set_user_state(
                user_id=user_id,
                state=request.state
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_me_state(
        self,
        request: SetUserStateRequest
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(status_code=401, detail="Unauthorized")
            user = await self.service.set_user_state(
                user_id=claims.user_id,
                state=request.state
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_status(
        self,
        user_id: str,
        request: SetUserStatusRequest
    ) -> Union[UserResponse, JSONResponse]:
        try:
            user = await self.service.set_user_status(
                user_id=user_id,
                status=request.status
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_user(self, user_id: str) -> Union[Response, JSONResponse]:
        try:
            message = await self.service.remove_user(user_id)
            return Response(content=message, status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)
