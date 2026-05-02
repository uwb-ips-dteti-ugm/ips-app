from typing import Optional, Tuple
from fastapi import Request, Response, status, HTTPException
from ips_app.ports.driving.http.auth import AuthHTTPPort
from ips_app.adapters.driving.http.dto.auth import (
    SignUpRequest,
    SignInRequest,
    RegisterRequest,
    SetNewPasswordRequest,
    SetNewPasswordWithOldPasswordRequest,
    SetAuthInfoRequest,
    RefreshTokenRequest,
    TokenResponse
)
from ips_app.adapters.driving.http.middleware.auth_jwt import get_claims
from ips_app.adapters.driving.http.dto.user import UserResponse

class AuthHandler:
    def __init__(self, service: AuthHTTPPort):
        self.service = service

    async def post_sign_up(self, request: SignUpRequest) -> TokenResponse:
        request.validate_fields()
        access_token, refresh_token = await self.service.sign_up(
            name=request.name,
            username=request.username,
            password=request.password
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def post_register(self, request: RegisterRequest) -> UserResponse:
        request.validate_fields()
        user = await self.service.register(
            name=request.name,
            username=request.username,
            password=request.password,
            role_id=request.role_id
        )
        return UserResponse.from_domain(user)

    async def post_sign_in(self, request: SignInRequest) -> TokenResponse:
        request.validate_fields()
        access_token, refresh_token = await self.service.sign_in(
            sign_in_identifier=request.sign_in_identifier,
            password=request.password
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def post_refresh_token(self, request: RefreshTokenRequest) -> TokenResponse:
        request.validate_fields()
        access_token, refresh_token = await self.service.refresh_token(request.refresh_token)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def post_sign_out(self) -> Response:
        claims = get_claims()
        if not claims:
            raise HTTPException(status_code=401, detail="Unauthorized")
            
        await self.service.sign_out(claims.user_id)
        return Response(content="Signed out successfully", status_code=status.HTTP_200_OK)

    async def patch_new_password(
        self,
        user_id: str,
        request: SetNewPasswordRequest
    ) -> Response:
        request.validate_fields()
        await self.service.set_new_password(
            user_id=user_id,
            new_password=request.new_password
        )
        return Response(content="Password set successfully", status_code=status.HTTP_200_OK)

    async def patch_auth_me_password(
        self,
        data: SetNewPasswordWithOldPasswordRequest
    ) -> Response:
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

    async def patch_auth_info(
        self,
        user_id: str,
        request: SetAuthInfoRequest
    ) -> Response:
        request.validate_fields()
        await self.service.set_auth_info(
            user_id=user_id,
            username=request.username
        )
        return Response(content="Auth info updated successfully", status_code=status.HTTP_200_OK)

    async def patch_auth_me_info(
        self,
        request: SetAuthInfoRequest
    ) -> Response:
        claims = get_claims()
        if not claims:
            raise HTTPException(status_code=401, detail="Unauthorized")
        request.validate_fields()

        await self.service.set_auth_info(
            user_id=claims.user_id,
            username=request.username
        )
        return Response(content="Auth info updated successfully", status_code=status.HTTP_200_OK)
