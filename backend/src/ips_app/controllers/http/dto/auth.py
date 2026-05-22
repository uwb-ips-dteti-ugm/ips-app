from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.domain.models.exception import ValidatorDomainException
from ips_app.utils.validator import (
    validate_name,
    validate_non_empty_string,
    validate_password,
    validate_username,
)


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


class SignInRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(..., examples=["johndoe"])
    password: str = Field(..., examples=["password123"])

    def validate_fields(self) -> None:
        validate_non_empty_string(self.username, "username")
        validate_non_empty_string(self.password, "password")


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(
        ...,
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )

    def validate_fields(self) -> None:
        validate_non_empty_string(self.refresh_token, "refresh_token")


class SetPasswordAuthRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Optional[str] = Field(None, examples=["newusername"])
    password: Optional[str] = Field(None, examples=["newsecurepass456"])

    def validate_fields(self) -> None:
        if self.username is None and self.password is None:
            raise ValidatorDomainException(
                "At least one of username or password must be provided."
            )
        if self.username is not None:
            validate_username(self.username)
        if self.password is not None:
            validate_password(self.password)


class SetPasswordAuthInfoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Optional[str] = Field(None, examples=["newusername"])

    def validate_fields(self) -> None:
        if self.username is None:
            raise ValidatorDomainException("username must be provided.")
        validate_username(self.username)


class SetPasswordWithOldPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    old_password: str = Field(..., examples=["password123"])
    new_password: str = Field(..., examples=["newsecurepass456"])

    def validate_fields(self) -> None:
        validate_non_empty_string(self.old_password, "old_password")
        validate_password(self.new_password)


class TokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    refresh_token: str = Field(
        ...,
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
