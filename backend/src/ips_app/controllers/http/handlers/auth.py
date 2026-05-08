from typing import Union

from fastapi import HTTPException, Response, status
from fastapi.responses import JSONResponse

from ips_app.controllers.http.dto.auth import (
    RefreshTokenRequest,
    RegisterRequest,
    SetAuthInfoRequest,
    SetNewPasswordRequest,
    SetNewPasswordWithOldPasswordRequest,
    SignInRequest,
    SignUpRequest,
    TokenResponse,
)
from ips_app.controllers.http.dto.user import UserResponse
from ips_app.controllers.http.handlers.exception import handle_exception
from ips_app.controllers.http.middlewares.auth_jwt import get_claims
from ips_app.domain.ports.driving.http.auth import AuthHTTP


class AuthHandler:
    def __init__(self, service: AuthHTTP):
        self.service = service

    def _handle_exception(self, error: Exception) -> JSONResponse:
        return handle_exception(error, domain_status_code=status.HTTP_401_UNAUTHORIZED)

    async def post_sign_up(
        self,
        request: SignUpRequest,
    ) -> Union[TokenResponse, JSONResponse]:
        try:
            request.validate_fields()
            access_token, refresh_token = await self.service.sign_up(
                name=request.name,
                username=request.username,
                password=request.password,
            )
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def post_register(
        self,
        request: RegisterRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            request.validate_fields()
            user = await self.service.register(
                name=request.name,
                username=request.username,
                password=request.password,
                role_id=request.role_id,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def post_sign_in(
        self,
        request: SignInRequest,
    ) -> Union[TokenResponse, JSONResponse]:
        try:
            request.validate_fields()
            access_token, refresh_token = await self.service.sign_in(
                sign_in_identifier=request.sign_in_identifier,
                password=request.password,
            )
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def post_refresh_token(
        self,
        request: RefreshTokenRequest,
    ) -> Union[TokenResponse, JSONResponse]:
        try:
            request.validate_fields()
            access_token, refresh_token = await self.service.refresh_token(
                request.refresh_token,
            )
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def post_sign_out(self) -> Union[Response, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            await self.service.sign_out(claims.user_id)
            return Response(
                content="Signed out successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def patch_new_password(
        self,
        user_id: str,
        request: SetNewPasswordRequest,
    ) -> Union[Response, JSONResponse]:
        try:
            request.validate_fields()
            await self.service.set_new_password(
                user_id=user_id,
                new_password=request.new_password,
            )
            return Response(
                content="Password set successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def patch_auth_me_password(
        self,
        request: SetNewPasswordWithOldPasswordRequest,
    ) -> Union[Response, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            request.validate_fields()
            await self.service.set_new_password_with_old_password(
                user_id=claims.user_id,
                old_password=request.old_password,
                new_password=request.new_password,
            )
            return Response(
                content="Password updated successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def patch_auth_info(
        self,
        user_id: str,
        request: SetAuthInfoRequest,
    ) -> Union[Response, JSONResponse]:
        try:
            request.validate_fields()
            await self.service.set_auth_info(
                user_id=user_id,
                username=request.username,
            )
            return Response(
                content="Auth info updated successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def patch_auth_me_info(
        self,
        request: SetAuthInfoRequest,
    ) -> Union[Response, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            request.validate_fields()
            await self.service.set_auth_info(
                user_id=claims.user_id,
                username=request.username,
            )
            return Response(
                content="Auth info updated successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self._handle_exception(e)
