from typing import Optional, Tuple, List, Any, Union
from fastapi import Request, Response, status, HTTPException
from fastapi.responses import JSONResponse
from ips_app_old.ports.driving.http.auth import AuthHTTPPort
from ips_app_old.domain.models.exception import (
    NotFoundException,
    DuplicateException,
    ValidatorException,
    DomainException,
)
from ips_app_old.adapters.driving.http.dto.auth import (
    SignUpRequest,
    SignInRequest,
    RegisterRequest,
    SetNewPasswordRequest,
    SetNewPasswordWithOldPasswordRequest,
    SetAuthInfoRequest,
    RefreshTokenRequest,
    TokenResponse,
    AuthUsersResponse
)
from ips_app_old.adapters.driving.http.dto.common import ErrorResponse
from ips_app_old.adapters.driving.http.middleware.auth_jwt import get_claims
from ips_app_old.adapters.driving.http.dto.user import UserResponse

class AuthHandler:
    def __init__(self, service: AuthHTTPPort):
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
        elif isinstance(e, DomainException):
            status_code = status.HTTP_401_UNAUTHORIZED
            message = str(e)
        elif isinstance(e, HTTPException):
            status_code = e.status_code
            message = str(e.detail)
        
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(error=message).model_dump()
        )

    async def post_sign_up(self, request: SignUpRequest) -> Union[TokenResponse, JSONResponse]:
        try:
            request.validate_fields()
            access_token, refresh_token = await self.service.sign_up(
                name=request.name,
                username=request.username,
                password=request.password
            )
            return TokenResponse(access_token=access_token, refresh_token=refresh_token)
        except Exception as e:
            return self._handle_exception(e)

    async def post_register(self, request: RegisterRequest) -> Union[UserResponse, JSONResponse]:
        try:
            request.validate_fields()
            user = await self.service.register(
                name=request.name,
                username=request.username,
                password=request.password,
                role_id=request.role_id
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def post_sign_in(self, request: SignInRequest) -> Union[TokenResponse, JSONResponse]:
        try:
            request.validate_fields()
            access_token, refresh_token = await self.service.sign_in(
                sign_in_identifier=request.sign_in_identifier,
                password=request.password
            )
            return TokenResponse(access_token=access_token, refresh_token=refresh_token)
        except Exception as e:
            return self._handle_exception(e)

    async def post_refresh_token(self, request: RefreshTokenRequest) -> Union[TokenResponse, JSONResponse]:
        try:
            request.validate_fields()
            access_token, refresh_token = await self.service.refresh_token(request.refresh_token)
            return TokenResponse(access_token=access_token, refresh_token=refresh_token)
        except Exception as e:
            return self._handle_exception(e)

    async def get_auths_users(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> Union[AuthUsersResponse, JSONResponse]:
        try:
            auths, users, total = await self.service.get_auths_users(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search
            )
            return AuthUsersResponse.from_domain(
                auths=auths,
                users=users,
                page=page,
                limit=limit,
                total=total
            )
        except Exception as e:
            return self._handle_exception(e)

    async def post_sign_out(self) -> Union[Response, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(status_code=401, detail="Unauthorized")
                
            await self.service.sign_out(claims.user_id)
            return Response(content="Signed out successfully", status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_new_password(
        self,
        user_id: str,
        request: SetNewPasswordRequest
    ) -> Union[Response, JSONResponse]:
        try:
            request.validate_fields()
            await self.service.set_new_password(
                user_id=user_id,
                new_password=request.new_password
            )
            return Response(content="Password set successfully", status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_auth_me_password(
        self,
        data: SetNewPasswordWithOldPasswordRequest
    ) -> Union[Response, JSONResponse]:
        try:
            data.validate_fields()
            claims = get_claims()
            if not claims:
                raise HTTPException(status_code=401, detail="Unauthorized")
                
            await self.service.set_new_password_with_old_password(
                user_id=claims.user_id,
                old_password=data.old_password,
                new_password=data.new_password
            )
            return Response(content="Password updated successfully", status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_auth_info(
        self,
        user_id: str,
        request: SetAuthInfoRequest
    ) -> Union[Response, JSONResponse]:
        try:
            request.validate_fields()
            await self.service.set_auth_info(
                user_id=user_id,
                username=request.username
            )
            return Response(content="Auth info updated successfully", status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_auth_me_info(
        self,
        request: SetAuthInfoRequest
    ) -> Union[Response, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(status_code=401, detail="Unauthorized")
            request.validate_fields()
            
            await self.service.set_auth_info(
                user_id=claims.user_id,
                username=request.username
            )
            return Response(content="Auth info updated successfully", status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)
