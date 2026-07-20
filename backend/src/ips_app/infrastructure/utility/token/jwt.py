from datetime import datetime, timedelta, timezone

import jwt

from ips_app.domain.contracts.utility.token import TokenIssuer
from ips_app.domain.models.exception import (
    DomainException,
    ExpiredTokenDomainException,
    InvalidTokenDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.user import UserAccessTokenClaims, UserRefreshTokenClaims


class JwtTokenIssuer(TokenIssuer):
    def __init__(
        self,
        access_secret: str,
        access_expiry: int,
        refresh_secret: str,
        refresh_expiry: int,
    ) -> None:
        self.access_secret = access_secret
        self.access_expiry = access_expiry
        self.refresh_secret = refresh_secret
        self.refresh_expiry = refresh_expiry

    def create_access_token(self, claims: UserAccessTokenClaims) -> str:
        try:
            return self._create_token(claims, self.access_secret, self.access_expiry)
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    def validate_access_token(self, token: str) -> UserAccessTokenClaims:
        try:
            payload = self._decode_token(token, self.access_secret)
            try:
                return UserAccessTokenClaims(
                    user_id=payload["user_id"],
                    role_id=payload["role_id"],
                    name=payload["name"],
                )
            except KeyError:
                # A well-signed token missing an expected claim (e.g. a refresh token
                # presented where an access token is expected) is an invalid token,
                # not an unexpected server error.
                raise InvalidTokenDomainException() from None
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    def create_refresh_token(self, claims: UserRefreshTokenClaims) -> str:
        try:
            return self._create_token(claims, self.refresh_secret, self.refresh_expiry)
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    def validate_refresh_token(self, token: str) -> UserRefreshTokenClaims:
        try:
            payload = self._decode_token(token, self.refresh_secret)
            try:
                return UserRefreshTokenClaims(user_id=payload["user_id"])
            except KeyError:
                raise InvalidTokenDomainException() from None
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    def _create_token(
        self,
        claims: UserAccessTokenClaims | UserRefreshTokenClaims,
        secret: str,
        expiry: int,
    ) -> str:
        payload = {
            **claims.model_dump(),
            "exp": datetime.now(timezone.utc) + timedelta(seconds=expiry),
        }
        return jwt.encode(payload, secret, algorithm="HS256")

    def _decode_token(self, token: str, secret: str) -> dict:
        try:
            return jwt.decode(token, secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenDomainException()
        except jwt.InvalidTokenError:
            raise InvalidTokenDomainException()
