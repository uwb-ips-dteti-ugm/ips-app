from pydantic import BaseModel, ConfigDict, Field


class SignInRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(..., examples=["alice"])
    password: str = Field(..., examples=["s3cr3t-password"])


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role_id: str
    name: str = Field(..., examples=["Alice"])
    username: str = Field(..., examples=["alice"])
    password: str = Field(..., examples=["s3cr3t-password"])
    bio: str = ""


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    old_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
