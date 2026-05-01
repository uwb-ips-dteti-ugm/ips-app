from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from ips_app.domain.models.user import UserAccessTokenClaims, UserRefreshTokenClaims
from ips_app.domain.models.exception import InvalidTokenException, ExpiredTokenException

_ACCESS_TOKEN_PRIVATE_KEY: Optional[str] = None
_ACCESS_TOKEN_EXPIRY: Optional[int] = None  # seconds

_REFRESH_TOKEN_PRIVATE_KEY: Optional[str] = None
_REFRESH_TOKEN_EXPIRY: Optional[int] = None  # seconds


def config_access_token(private_key: str, expiry: int) -> None:
    global _ACCESS_TOKEN_PRIVATE_KEY, _ACCESS_TOKEN_EXPIRY
    _ACCESS_TOKEN_PRIVATE_KEY = private_key
    _ACCESS_TOKEN_EXPIRY = expiry


def config_refresh_token(private_key: str, expiry: int) -> None:
    global _REFRESH_TOKEN_PRIVATE_KEY, _REFRESH_TOKEN_EXPIRY
    _REFRESH_TOKEN_PRIVATE_KEY = private_key
    _REFRESH_TOKEN_EXPIRY = expiry


def create_access_token(claims: UserAccessTokenClaims) -> str:
    if _ACCESS_TOKEN_PRIVATE_KEY is None or _ACCESS_TOKEN_EXPIRY is None:
        raise RuntimeError("Access token is not configured. Call config_access_token first.")
    payload = {
        **claims.model_dump(),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=_ACCESS_TOKEN_EXPIRY),
    }
    return jwt.encode(payload, _ACCESS_TOKEN_PRIVATE_KEY, algorithm="HS256")


def create_refresh_token(claims: UserRefreshTokenClaims) -> str:
    if _REFRESH_TOKEN_PRIVATE_KEY is None or _REFRESH_TOKEN_EXPIRY is None:
        raise RuntimeError("Refresh token is not configured. Call config_refresh_token first.")
    payload = {
        **claims.model_dump(),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=_REFRESH_TOKEN_EXPIRY),
    }
    return jwt.encode(payload, _REFRESH_TOKEN_PRIVATE_KEY, algorithm="HS256")


def validate_access_token(token: str) -> UserAccessTokenClaims:
    if _ACCESS_TOKEN_PRIVATE_KEY is None:
        raise RuntimeError("Access token is not configured. Call config_access_token first.")
    try:
        payload = jwt.decode(token, _ACCESS_TOKEN_PRIVATE_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()
    return UserAccessTokenClaims(
        user_id=payload["user_id"],
        name=payload["name"],
        role_id=payload["role_id"],
    )


def validate_refresh_token(token: str) -> UserRefreshTokenClaims:
    if _REFRESH_TOKEN_PRIVATE_KEY is None:
        raise RuntimeError("Refresh token is not configured. Call config_refresh_token first.")
    try:
        payload = jwt.decode(token, _REFRESH_TOKEN_PRIVATE_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()
    return UserRefreshTokenClaims(user_id=payload["user_id"])
