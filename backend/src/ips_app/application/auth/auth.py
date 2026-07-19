from typing import Any, Optional, Tuple

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.repository.user import UserRepository
from ips_app.domain.contracts.utility.password import PasswordHasher
from ips_app.domain.contracts.utility.token import TokenIssuer
from ips_app.domain.models.exception import (
    DomainException,
    ForbiddenDomainException,
    InvalidCredentialsDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.user import (
    User,
    UserAccessTokenClaims,
    UserRefreshTokenClaims,
    UserStatus,
)
from ips_app.domain.usecases.auth import AuthUsecase

from ips_app.application._shared.validator import (
    validate_non_empty_string,
    validate_password,
)


class BaseAuthUsecase(AuthUsecase):
    def __init__(
        self,
        repo: UserRepository,
        password_hasher: PasswordHasher,
        token_issuer: TokenIssuer,
        log: LeveledLogger,
    ) -> None:
        self.repo = repo
        self.password_hasher = password_hasher
        self.token_issuer = token_issuer
        self.log = log
        self.tag_class = self.__class__.__name__

    async def sign_in(self, username: str, password: str) -> Tuple[str, str]:
        tag = f"{self.tag_class}/sign_in"
        try:
            validate_non_empty_string(username, "username")
            validate_non_empty_string(password, "password")

            user = await self.repo.read_user_by_username(username)
            if not self.password_hasher.verify(password, user.password_hash):
                raise InvalidCredentialsDomainException()
            self._ensure_user_can_authenticate(user)

            tokens = self._generate_tokens(user)
            await self.log.info(
                tag, "Successfully signed in user", {"id": str(user.id), "username": username}
            )
            return tokens
        except Exception as e:
            await self.log.error(
                tag, "Failed to sign in user", {"error": str(e), "username": username}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        tag = f"{self.tag_class}/refresh_token"
        try:
            validate_non_empty_string(refresh_token, "refresh_token")

            claims = self.token_issuer.validate_refresh_token(refresh_token)
            user = await self.repo.read_user_by_id(claims.user_id)
            self._ensure_user_can_authenticate(user)

            tokens = self._generate_tokens(user)
            await self.log.info(
                tag, "Successfully refreshed token", {"id": str(user.id)}
            )
            return tokens
        except Exception as e:
            await self.log.error(tag, "Failed to refresh token", {"error": str(e)})
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def change_password(
        self,
        user_id: Any,
        old_password: str,
        new_password: str,
        updated_by: Optional[Any] = None,
    ) -> None:
        tag = f"{self.tag_class}/change_password"
        try:
            validate_non_empty_string(old_password, "old_password")
            validate_password(new_password)

            user = await self.repo.read_user_by_id(user_id)
            if not self.password_hasher.verify(old_password, user.password_hash):
                raise InvalidCredentialsDomainException()

            password_hash = self.password_hasher.hash(new_password)
            await self.repo.update_user_password_by_id(
                id=user_id,
                password_hash=password_hash,
                updated_by=updated_by,
            )
            await self.log.info(
                tag, "Successfully changed password", {"id": str(user_id)}
            )
        except Exception as e:
            await self.log.error(
                tag, "Failed to change password", {"error": str(e), "id": str(user_id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def reset_password(
        self,
        user_id: Any,
        new_password: str,
        updated_by: Optional[Any] = None,
    ) -> None:
        tag = f"{self.tag_class}/reset_password"
        try:
            validate_password(new_password)

            password_hash = self.password_hasher.hash(new_password)
            await self.repo.update_user_password_by_id(
                id=user_id,
                password_hash=password_hash,
                updated_by=updated_by,
            )
            await self.log.info(
                tag, "Successfully reset password", {"id": str(user_id)}
            )
        except Exception as e:
            await self.log.error(
                tag, "Failed to reset password", {"error": str(e), "id": str(user_id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    def _ensure_user_can_authenticate(self, user: User) -> None:
        if user.status == UserStatus.SUSPENDED:
            raise ForbiddenDomainException("User is suspended.")
        if user.status == UserStatus.BANNED:
            raise ForbiddenDomainException("User is banned.")

    def _generate_tokens(self, user: User) -> Tuple[str, str]:
        access_claims = UserAccessTokenClaims(
            user_id=str(user.id),
            role_id=str(user.role.id) if user.role.id is not None else "",
            name=user.name,
        )
        refresh_claims = UserRefreshTokenClaims(user_id=str(user.id))
        access_token = self.token_issuer.create_access_token(access_claims)
        refresh_token = self.token_issuer.create_refresh_token(refresh_claims)
        return access_token, refresh_token
