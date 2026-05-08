from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, Any
from pydantic import BaseModel, Field
from ips_app_old.utils.validator import validate_name, validate_username, validate_password
from ips_app_old.adapters.driving.http.dto.common import PaginationMeta
from ips_app_old.adapters.driving.http.dto.user import UserResponse

if TYPE_CHECKING:
    from ips_app_old.domain.models.auth import Auth
    from ips_app_old.domain.models.user import User


class SignUpRequest(BaseModel):
    name: str = Field(..., examples=["John Doe"])
    username: str = Field(..., examples=["johndoe"])
    password: str = Field(..., examples=["password123"])

    def validate_fields(self) -> None:
        validate_name(self.name)
        validate_username(self.username)
        validate_password(self.password)


class SignInRequest(BaseModel):
    sign_in_identifier: str = Field(..., examples=["johndoe"])
    password: str = Field(..., examples=["password123"])

    def validate_fields(self) -> None:
        if not self.sign_in_identifier.strip():
            raise ValueError("sign_in_identifier must not be empty.")
        if not self.password:
            raise ValueError("password must not be empty.")


class RegisterRequest(BaseModel):
    name: str = Field(..., examples=["Jane Smith"])
    username: str = Field(..., examples=["janesmith"])
    password: str = Field(..., examples=["securepass123"])
    role_id: str = Field(..., examples=["507f1f77bcf86cd799439011"])

    def validate_fields(self) -> None:
        validate_name(self.name)
        validate_username(self.username)
        validate_password(self.password)
        if not self.role_id.strip():
            raise ValueError("role_id must not be empty.")


class SetNewPasswordRequest(BaseModel):
    new_password: str = Field(..., examples=["newsecurepass456"])

    def validate_fields(self) -> None:
        validate_password(self.new_password)


class SetNewPasswordWithOldPasswordRequest(BaseModel):
    old_password: str = Field(..., examples=["password123"])
    new_password: str = Field(..., examples=["newsecurepass456"])

    def validate_fields(self) -> None:
        if not self.old_password:
            raise ValueError("old_password must not be empty.")
        validate_password(self.new_password)


class SetAuthInfoRequest(BaseModel):
    username: Optional[str] = Field(None, examples=["newusername"])

    def validate_fields(self) -> None:
        if self.username is not None:
            validate_username(self.username)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])

    def validate_fields(self) -> None:
        if not self.refresh_token:
            raise ValueError("refresh_token must not be empty.")


class TokenResponse(BaseModel):
    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    refresh_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])


class AuthUserResponse(BaseModel):
    auth_id: str = Field(..., examples=["507f1f77bcf86cd799439011"])
    username: str = Field(..., examples=["johndoe"])
    user: UserResponse

    @classmethod
    def from_domain(cls, auth: Auth, user: User) -> AuthUserResponse:
        return cls(
            auth_id=str(auth.id),
            username=auth.username,
            user=UserResponse.from_domain(user)
        )


class AuthUsersResponse(BaseModel):
    data: List[AuthUserResponse]
    meta: PaginationMeta

    @classmethod
    def from_domain(
        cls,
        auths: List[Auth],
        users: List[User],
        page: int,
        limit: int,
        total: int,
    ) -> AuthUsersResponse:
        return cls(
            data=[AuthUserResponse.from_domain(a, u) for a, u in zip(auths, users)],
            meta=PaginationMeta(page=page, limit=limit, total=total),
        )

# Rebuild models to resolve forward references for Pydantic/FastAPI schema generation
AuthUserResponse.model_rebuild()
AuthUsersResponse.model_rebuild()
