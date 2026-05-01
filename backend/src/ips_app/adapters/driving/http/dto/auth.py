from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from ips_app.utils.validator import validate_name, validate_username, validate_password

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

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
