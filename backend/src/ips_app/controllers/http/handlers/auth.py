from typing import Union

from fastapi import HTTPException, Response, status
from fastapi.responses import JSONResponse

from ips_app.controllers.http.dto.auth import (
    RefreshTokenRequest,
    RegisterRequest,
    SetPasswordAuthInfoRequest,
    SetPasswordAuthRequest,
    SetPasswordWithOldPasswordRequest,
    SignInRequest,
    TokenResponse,
)
from ips_app.controllers.http.dto.common import ErrorResponse
from ips_app.controllers.http.dto.user import UserResponse
from ips_app.controllers.http.middlewares.auth_jwt import get_claims
from ips_app.domain.models.exception import (
    DuplicateDomainException,
    ExpiredTokenDomainException,
    ForbiddenDomainException,
    InvalidCredentialsDomainException,
    InvalidTokenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.ports.driving.http.auth import AuthHTTP


class AuthHandler:
    def __init__(self, service: AuthHTTP):
        self.service = service

    async def post_register(
        self,
        request: RegisterRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            user = await self.service.register(
                name=request.name,
                username=request.username,
                password=request.password,
                role_id=request.role_id,
                created_by=claims.user_id if claims else None,
            )
            return UserResponse.from_domain(user)
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
                        error="That username is already taken. Please use a different username."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The selected role does not exist. Please choose another role."
                    ).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error="You do not have permission to register users."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while registering the user. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while registering the user. Please try again."
                ).model_dump(),
            )

    async def post_sign_in(
        self,
        request: SignInRequest,
    ) -> Union[TokenResponse, JSONResponse]:
        try:
            request.validate_fields()
            access_token, refresh_token = await self.service.sign_in(
                username=request.username,
                password=request.password,
            )
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
            )
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, InvalidCredentialsDomainException):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content=ErrorResponse(
                        error="The username or password is incorrect."
                    ).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                message = str(e).lower()
                if "suspended" in message:
                    error = "Your account is suspended. Please contact an administrator."
                elif "banned" in message:
                    error = "Your account is banned. Please contact an administrator."
                else:
                    error = "You cannot sign in with this account. Please contact an administrator."
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content=ErrorResponse(
                        error="The username or password is incorrect."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while signing in. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while signing in. Please try again."
                ).model_dump(),
            )

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
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, ExpiredTokenDomainException):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content=ErrorResponse(
                        error="Your session has expired. Please sign in again."
                    ).model_dump(),
                )
            if isinstance(e, InvalidTokenDomainException):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content=ErrorResponse(
                        error="Your session is invalid. Please sign in again."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="Your account could not be found. Please sign in again."
                    ).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                message = str(e).lower()
                if "suspended" in message:
                    error = "Your account is suspended. Please contact an administrator."
                elif "banned" in message:
                    error = "Your account is banned. Please contact an administrator."
                else:
                    error = "Your session cannot be refreshed. Please sign in again."
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while refreshing your session. Please sign in again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while refreshing your session. Please sign in again."
                ).model_dump(),
            )

    async def patch_user_password_auth(
        self,
        user_id: str,
        request: SetPasswordAuthRequest,
    ) -> Union[Response, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            await self.service.set_password_auth(
                user_id=user_id,
                username=request.username,
                password=request.password,
                updated_by=claims.user_id if claims else None,
            )
            return Response(
                content="Password auth updated successfully",
                status_code=status.HTTP_200_OK,
            )
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
                        error="That username is already taken. Please use a different username."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                if e.group_name == "auths":
                    error = "This user does not have password sign-in enabled yet."
                else:
                    error = "The selected user does not exist."
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error="You do not have permission to update this user's sign-in settings."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating password sign-in. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating password sign-in. Please try again."
                ).model_dump(),
            )

    async def patch_auth_me_info(
        self,
        request: SetPasswordAuthInfoRequest,
    ) -> Union[Response, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content=ErrorResponse(
                        error="Please sign in to continue."
                    ).model_dump(),
                )
            request.validate_fields()
            await self.service.set_password_auth(
                user_id=claims.user_id,
                username=request.username,
                updated_by=claims.user_id,
            )
            return Response(
                content="Auth info updated successfully",
                status_code=status.HTTP_200_OK,
            )
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
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, DuplicateDomainException):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content=ErrorResponse(
                        error="That username is already taken. Please use a different username."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                if e.group_name == "auths":
                    error = "Your account does not have password sign-in enabled yet."
                else:
                    error = "Your account could not be found. Please sign in again."
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating your sign-in information. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating your sign-in information. Please try again."
                ).model_dump(),
            )

    async def patch_auth_me_password(
        self,
        request: SetPasswordWithOldPasswordRequest,
    ) -> Union[Response, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content=ErrorResponse(
                        error="Please sign in to continue."
                    ).model_dump(),
                )
            request.validate_fields()
            await self.service.set_password_with_old_password(
                user_id=claims.user_id,
                old_password=request.old_password,
                new_password=request.new_password,
                updated_by=claims.user_id,
            )
            return Response(
                content="Password updated successfully",
                status_code=status.HTTP_200_OK,
            )
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
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, InvalidCredentialsDomainException):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content=ErrorResponse(
                        error="The current password is incorrect."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                if e.group_name == "auths":
                    error = "Your account does not have password sign-in enabled yet."
                else:
                    error = "Your account could not be found. Please sign in again."
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating your password. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating your password. Please try again."
                ).model_dump(),
            )
