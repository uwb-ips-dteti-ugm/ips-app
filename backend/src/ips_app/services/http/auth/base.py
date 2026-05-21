from typing import Any, Optional, Tuple

from ips_app.domain.models.exception import (
    DomainException,
    ForbiddenDomainException,
    InvalidCredentialsDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.user import (
    User,
    UserAccessTokenClaims,
    UserPasswordAuth,
    UserRefreshTokenClaims,
    UserStatus,
)
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.user import UserRepository
from ips_app.domain.ports.driving.http.auth import AuthHTTP
from ips_app.utils.password import hash_password, verify_password
from ips_app.utils.token import (
    create_access_token,
    create_refresh_token,
    validate_refresh_token,
)


class BaseAuthHTTP(AuthHTTP):
    def __init__(
        self,
        repo_user: UserRepository,
        log: LeveledLogging,
    ):
        self.repo_user = repo_user
        self.log = log
        self.tag_class = self.__class__.__name__

    async def register(
        self,
        name: str,
        username: str,
        password: str,
        role_id: Any,
        created_by: Optional[Any] = None,
    ) -> User:
        tag = f"{self.tag_class}.register"
        try:
            user = await self.repo_user.create_user(
                role_id=role_id,
                name=name,
                created_by=created_by,
            )
            try:
                await self.repo_user.add_user_auth_by_id(
                    id=user.id,
                    auth=self._build_password_auth(username, password, created_by),
                    updated_by=created_by,
                )
            except DomainException:
                await self._delete_created_user(user.id, tag)
                raise

            full_user = await self.repo_user.read_user_by_id(user.id)
            await self.log.info(
                tag,
                "Successfully registered user via admin",
                {
                    "user_id": str(full_user.id),
                    "username": username,
                    "role_id": str(role_id),
                },
            )
            return full_user
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to register user via admin",
                {"error": str(e), "username": username},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def sign_in(
        self,
        username: str,
        password: str,
    ) -> Tuple[str, str]:
        tag = f"{self.tag_class}.sign_in"
        try:
            user = await self._read_password_user_by_username(username)
            auth = self._require_password_auth(user, hide_missing=True)
            if not verify_password(password, auth.password_hash):
                raise InvalidCredentialsDomainException()

            self._ensure_user_can_authenticate(user)
            full_user = await self.repo_user.read_user_by_id(user.id)
            await self.log.info(
                tag,
                "Successfully signed in user",
                {"user_id": str(full_user.id), "username": username},
            )
            return self._generate_tokens(full_user)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to sign in",
                {"error": str(e), "username": username},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        tag = f"{self.tag_class}.refresh_token"
        try:
            claims = validate_refresh_token(refresh_token)
            user = await self.repo_user.read_user_by_id(claims.user_id)
            self._ensure_user_can_authenticate(user)

            await self.log.info(
                tag,
                "Successfully refreshed token",
                {"user_id": str(user.id)},
            )
            return self._generate_tokens(user)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to refresh token",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_password_auth(
        self,
        user_id: Any,
        username: Optional[str] = None,
        password: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> None:
        tag = f"{self.tag_class}.set_password_auth"
        try:
            await self.repo_user.update_user_password_auth_by_id(
                id=user_id,
                username=username,
                password_hash=hash_password(password) if password is not None else None,
                updated_by=updated_by,
            )
            await self.log.info(
                tag,
                "Successfully updated password auth",
                {"user_id": str(user_id), "username": username},
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update password auth",
                {"error": str(e), "user_id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_password_with_old_password(
        self,
        user_id: Any,
        old_password: str,
        new_password: str,
        updated_by: Optional[Any] = None,
    ) -> None:
        tag = f"{self.tag_class}.set_password_with_old_password"
        try:
            user = await self.repo_user.read_user_by_id(user_id)
            auth = self._require_password_auth(user)
            if not verify_password(old_password, auth.password_hash):
                raise InvalidCredentialsDomainException()

            await self.repo_user.update_user_password_auth_by_id(
                id=user_id,
                password_hash=hash_password(new_password),
                updated_by=updated_by,
            )
            await self.log.info(
                tag,
                "Successfully updated password",
                {"user_id": str(user_id)},
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update password",
                {"error": str(e), "user_id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    def _build_password_auth(
        self,
        username: str,
        password: str,
        created_by: Optional[Any] = None,
    ) -> UserPasswordAuth:
        return UserPasswordAuth(
            username=username,
            password_hash=hash_password(password),
            created_by=created_by,
        )

    async def _read_password_user_by_username(self, username: str) -> User:
        try:
            return await self.repo_user.read_user_by_password_username(username)
        except NotFoundDomainException:
            raise InvalidCredentialsDomainException() from None

    def _require_password_auth(
        self,
        user: User,
        hide_missing: bool = False,
    ) -> UserPasswordAuth:
        auth = user.password_auth
        if auth is None:
            if hide_missing:
                raise InvalidCredentialsDomainException()
            raise NotFoundDomainException("password", "auths")
        return auth

    def _generate_tokens(self, user: User) -> Tuple[str, str]:
        access_claims = UserAccessTokenClaims(
            user_id=str(user.id),
            name=user.name,
            role_id=str(user.role.id) if user.role.id is not None else "",
        )
        refresh_claims = UserRefreshTokenClaims(user_id=str(user.id))
        return create_access_token(access_claims), create_refresh_token(refresh_claims)

    def _ensure_user_can_authenticate(self, user: User) -> None:
        if user.status == UserStatus.SUSPENDED:
            raise ForbiddenDomainException("User is suspended.")
        if user.status == UserStatus.BANNED:
            raise ForbiddenDomainException("User is banned.")

    async def _delete_created_user(self, user_id: Any, tag: str) -> None:
        try:
            await self.repo_user.delete_user_by_id(user_id)
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to roll back created user after auth add failure",
                {"error": str(e), "user_id": str(user_id)},
            )
