from typing import Optional

from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.auth import AuthUsecase
from ips_app.domain.usecases.user import UserUsecase
from ips_app.presentation.http.dto.auth import (
    ChangePasswordRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SignInRequest,
    TokenResponse,
)
from ips_app.presentation.http.dto.common import MessageResponse
from ips_app.presentation.http.dto.user import UserResponse


class AuthHandler:
    def __init__(self, auth_usecase: AuthUsecase, user_usecase: UserUsecase) -> None:
        self.auth_usecase = auth_usecase
        self.user_usecase = user_usecase

    async def post_sign_in(self, request: SignInRequest) -> TokenResponse:
        access_token, refresh_token = await self.auth_usecase.sign_in(
            username=request.username, password=request.password
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def post_refresh_token(self, request: RefreshTokenRequest) -> TokenResponse:
        access_token, refresh_token = await self.auth_usecase.refresh_token(
            request.refresh_token
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def post_register(
        self,
        request: RegisterRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> UserResponse:
        user = await self.user_usecase.create_user(
            role_id=request.role_id,
            name=request.name,
            username=request.username,
            password=request.password,
            bio=request.bio,
            created_by=claims.user_id if claims else None,
        )
        return UserResponse.from_domain(user)

    async def patch_auth_me_password(
        self,
        request: ChangePasswordRequest,
        claims: UserAccessTokenClaims,
    ) -> MessageResponse:
        await self.auth_usecase.change_password(
            user_id=claims.user_id,
            old_password=request.old_password,
            new_password=request.new_password,
            updated_by=claims.user_id,
        )
        return MessageResponse(message="Password changed successfully.")

    async def patch_user_password(
        self,
        user_id: str,
        request: ResetPasswordRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> MessageResponse:
        await self.auth_usecase.reset_password(
            user_id=user_id,
            new_password=request.new_password,
            updated_by=claims.user_id if claims else None,
        )
        return MessageResponse(message="Password reset successfully.")
