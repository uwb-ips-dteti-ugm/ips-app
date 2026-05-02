from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel
from ips_app.utils.validator import validate_name, validate_username, validate_password
from ips_app.adapters.driving.http.dto.common import PaginationMeta

if TYPE_CHECKING:
    from ips_app.domain.models.auth import Auth
    from ips_app.domain.models.user import User
    from ips_app.adapters.driving.http.dto.user import UserResponse


class SignUpRequest(BaseModel):
    name: str
    username: str
    password: str

    def validate_fields(self) -> None:
        validate_name(self.name)
        validate_username(self.username)
        validate_password(self.password)


class SignInRequest(BaseModel):
    sign_in_identifier: str
    password: str

    def validate_fields(self) -> None:
        if not self.sign_in_identifier.strip():
            raise ValueError("sign_in_identifier must not be empty.")
        if not self.password:
            raise ValueError("password must not be empty.")


class RegisterRequest(BaseModel):
    name: str
    username: str
    password: str
    role_id: str

    def validate_fields(self) -> None:
        validate_name(self.name)
        validate_username(self.username)
        validate_password(self.password)
        if not self.role_id.strip():
            raise ValueError("role_id must not be empty.")


class SetNewPasswordRequest(BaseModel):
    new_password: str

    def validate_fields(self) -> None:
        validate_password(self.new_password)


class SetNewPasswordWithOldPasswordRequest(BaseModel):
    old_password: str
    new_password: str

    def validate_fields(self) -> None:
        if not self.old_password:
            raise ValueError("old_password must not be empty.")
        validate_password(self.new_password)


class SetAuthInfoRequest(BaseModel):
    username: Optional[str] = None

    def validate_fields(self) -> None:
        if self.username is not None:
            validate_username(self.username)


class RefreshTokenRequest(BaseModel):
    refresh_token: str

    def validate_fields(self) -> None:
        if not self.refresh_token:
            raise ValueError("refresh_token must not be empty.")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class AuthUserResponse(BaseModel):
    auth_id: str
    username: str
    user: UserResponse

    @classmethod
    def from_domain(cls, auth: Auth, user: User) -> AuthUserResponse:
        from ips_app.adapters.driving.http.dto.user import UserResponse
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
