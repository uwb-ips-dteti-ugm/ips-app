from abc import ABC, abstractmethod

from ips_app.domain.models.user import UserAccessTokenClaims, UserRefreshTokenClaims


class TokenIssuer(ABC):
    @abstractmethod
    def create_access_token(self, claims: UserAccessTokenClaims) -> str: ...

    @abstractmethod
    def validate_access_token(self, token: str) -> UserAccessTokenClaims: ...

    @abstractmethod
    def create_refresh_token(self, claims: UserRefreshTokenClaims) -> str: ...

    @abstractmethod
    def validate_refresh_token(self, token: str) -> UserRefreshTokenClaims: ...
