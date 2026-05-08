from __future__ import annotations

from datetime import datetime
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from ips_app.controllers.http.dto.common import (
    PaginationMeta,
    validate_non_empty_string,
)
from ips_app.controllers.http.dto.user import UserResponse
from ips_app.domain.models.exception import ValidatorDomainException
from ips_app.domain.models.user import User, UserAuthType, UserPasswordAuth
from ips_app.utils.validator import validate_name, validate_password, validate_username


class SignUpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., examples=["John Doe"])
    username: str = Field(..., examples=["johndoe"])
    password: str = Field(..., examples=["password123"])

    def validate_fields(self) -> None:
        validate_name(self.name)
        validate_username(self.username)
        validate_password(self.password)


class SignInRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sign_in_identifier: str = Field(..., examples=["johndoe"])
    password: str = Field(..., examples=["password123"])

    def validate_fields(self) -> None:
        validate_non_empty_string(self.sign_in_identifier, "sign_in_identifier")
        validate_non_empty_string(self.password, "password")


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., examples=["Jane Smith"])
    username: str = Field(..., examples=["janesmith"])
    password: str = Field(..., examples=["securepass123"])
    role_id: str = Field(..., examples=["507f1f77bcf86cd799439011"])

    def validate_fields(self) -> None:
        validate_name(self.name)
        validate_username(self.username)
        validate_password(self.password)
        validate_non_empty_string(self.role_id, "role_id")


class SetNewPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    new_password: str = Field(..., examples=["newsecurepass456"])

    def validate_fields(self) -> None:
        validate_password(self.new_password)


class SetNewPasswordWithOldPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    old_password: str = Field(..., examples=["password123"])
    new_password: str = Field(..., examples=["newsecurepass456"])

    def validate_fields(self) -> None:
        validate_non_empty_string(self.old_password, "old_password")
        validate_password(self.new_password)


class SetAuthInfoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Optional[str] = Field(None, examples=["newusername"])

    def validate_fields(self) -> None:
        if self.username is not None:
            validate_username(self.username)


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(
        ...,
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )

    def validate_fields(self) -> None:
        validate_non_empty_string(self.refresh_token, "refresh_token")


class TokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    refresh_token: str = Field(
        ...,
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )


class UserPasswordAuthResponse(BaseModel):
    type: Literal[UserAuthType.PASSWORD] = UserAuthType.PASSWORD
    username: str = Field(..., examples=["johndoe"])
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_domain(cls, auth: UserPasswordAuth) -> UserPasswordAuthResponse:
        return cls(
            username=auth.username,
            created_at=auth.created_at,
            updated_at=auth.updated_at,
        )


UserAuthResponse = Annotated[
    Union[
        UserPasswordAuthResponse,
    ],
    Field(discriminator="type"),
]


class AuthUserResponse(BaseModel):
    user_id: str = Field(..., examples=["507f1f77bcf86cd799439011"])
    username: Optional[str] = Field(None, examples=["johndoe"])
    auths: List[UserAuthResponse] = Field(default_factory=list)
    user: UserResponse

    @classmethod
    def from_domain(cls, user: User) -> AuthUserResponse:
        password_auth = user.password_auth
        return cls(
            user_id=str(user.id),
            username=password_auth.username if password_auth else None,
            auths=[_auth_response_from_domain(auth) for auth in user.auths],
            user=UserResponse.from_domain(user),
        )


class AuthUsersResponse(BaseModel):
    data: List[AuthUserResponse]
    meta: PaginationMeta

    @classmethod
    def from_domain(
        cls,
        items: List[User],
        page: int,
        limit: int,
        total: int,
    ) -> AuthUsersResponse:
        return cls(
            data=[AuthUserResponse.from_domain(user) for user in items],
            meta=PaginationMeta(page=page, limit=limit, total=total),
        )


def _auth_response_from_domain(auth: object) -> UserAuthResponse:
    if isinstance(auth, UserPasswordAuth):
        return UserPasswordAuthResponse.from_domain(auth)
    raise ValidatorDomainException(f"Unsupported auth response type: {type(auth).__name__}")
