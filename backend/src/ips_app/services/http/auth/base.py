from typing import Any, Optional, Tuple

from ips_app.domain.models.exception import (
    DomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.user import (
    User,
    UserAccessTokenClaims,
    UserPasswordAuth,
    UserRefreshTokenClaims,
    UserState,
    UserStatus,
)
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.repository.role import RoleRepository
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
        repo_role: RoleRepository,
        log: GenericLogging,
    ):
        self.repo_user = repo_user
        self.repo_role = repo_role
        self.log = log
        self.tag_class = self.__class__.__name__

    async def sign_up(
        self,
        name: str,
        username: str,
        password: str,
    ) -> Tuple[str, str]:
        tag = f"{self.tag_class}.sign_up"
        try:
            default_role = await self.repo_role.read_role_default()
            auth = self._build_password_auth(username, password)

            user = await self.repo_user.create_user(
                role_id=default_role.id,
                name=name,
                auths=[auth],
            )

            await self.repo_user.update_user_last_signed_in_at_by_id(user.id)
            await self.repo_user.update_user_last_activity_at_by_id(user.id)
            await self._set_user_online_unless_dnd(user)
            full_user = await self.repo_user.read_user_by_id(user.id)

            await self.log.info(
                tag,
                "Successfully signed up user",
                {"user_id": str(full_user.id), "username": username},
            )
            return self._generate_tokens(full_user)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to sign up",
                {"error": str(e), "username": username},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def register(
        self,
        name: str,
        username: str,
        password: str,
        role_id: Any,
    ) -> User:
        tag = f"{self.tag_class}.register"
        try:
            auth = self._build_password_auth(username, password)

            user = await self.repo_user.create_user(
                role_id=role_id,
                name=name,
                auths=[auth],
            )

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
        sign_in_identifier: str,
        password: str,
    ) -> Tuple[str, str]:
        tag = f"{self.tag_class}.sign_in"
        try:
            user = await self._read_password_user_by_identifier(sign_in_identifier)
            auth = self._require_password_auth(user, hide_missing=True)
            if not verify_password(password, auth.password_hash):
                raise DomainException("Invalid credentials")

            self._ensure_user_can_authenticate(user)
            await self.repo_user.update_user_last_signed_in_at_by_id(user.id)
            await self.repo_user.update_user_last_activity_at_by_id(user.id)
            await self._set_user_online_unless_dnd(user)
            full_user = await self.repo_user.read_user_by_id(user.id)

            await self.log.info(
                tag,
                "Successfully signed in user",
                {"user_id": str(full_user.id), "username": sign_in_identifier},
            )
            return self._generate_tokens(full_user)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to sign in",
                {"error": str(e), "identifier": sign_in_identifier},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        tag = f"{self.tag_class}.refresh_token"
        try:
            claims = validate_refresh_token(refresh_token)
            user = await self.repo_user.read_user_by_id(claims.user_id)

            self._ensure_user_can_authenticate(user)
            await self.repo_user.update_user_last_refreshed_at_by_id(user.id)
            await self.repo_user.update_user_last_activity_at_by_id(user.id)
            await self._set_user_online_unless_dnd(user)
            full_user = await self.repo_user.read_user_by_id(user.id)

            await self.log.info(
                tag,
                "Successfully refreshed token",
                {"user_id": str(full_user.id)},
            )
            return self._generate_tokens(full_user)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to refresh token",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def sign_out(self, user_id: Any) -> None:
        tag = f"{self.tag_class}.sign_out"
        try:
            await self.repo_user.update_user_state_by_id(user_id, UserState.OFFLINE)
            await self.log.info(
                tag,
                "Successfully signed out user",
                {"user_id": str(user_id)},
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to sign out",
                {"error": str(e), "user_id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_new_password(self, user_id: Any, new_password: str) -> None:
        tag = f"{self.tag_class}.set_new_password"
        try:
            await self.repo_user.update_user_password_auth_password_by_id(
                user_id,
                hash_password(new_password),
            )
            await self.log.info(
                tag,
                "Successfully force-set password",
                {"user_id": str(user_id)},
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to force-set password",
                {"error": str(e), "user_id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_new_password_with_old_password(
        self,
        user_id: Any,
        old_password: str,
        new_password: str,
    ) -> None:
        tag = f"{self.tag_class}.set_new_password_with_old_password"
        try:
            user = await self.repo_user.read_user_by_id(user_id)
            auth = self._require_password_auth(user)
            if not verify_password(old_password, auth.password_hash):
                raise DomainException("Invalid credentials")

            await self.repo_user.update_user_password_auth_password_by_id(
                user_id,
                hash_password(new_password),
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

    async def set_auth_info(self, user_id: Any, username: Optional[str] = None) -> None:
        tag = f"{self.tag_class}.set_auth_info"
        try:
            await self.repo_user.update_user_password_auth_info_by_id(
                user_id,
                username=username,
            )
            await self.log.info(
                tag,
                "Successfully updated auth info",
                {"user_id": str(user_id), "username": username},
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update auth info",
                {"error": str(e), "user_id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    def _build_password_auth(self, username: str, password: str) -> UserPasswordAuth:
        return UserPasswordAuth(
            username=username,
            password_hash=hash_password(password),
        )

    async def _read_password_user_by_identifier(self, identifier: str) -> User:
        try:
            return await self.repo_user.read_user_by_username(identifier)
        except NotFoundDomainException:
            raise DomainException("Invalid credentials") from None

    def _require_password_auth(
        self,
        user: User,
        hide_missing: bool = False,
    ) -> UserPasswordAuth:
        auth = user.password_auth
        if auth is None:
            if hide_missing:
                raise DomainException("Invalid credentials")
            raise NotFoundDomainException("password", "auths")
        return auth

    def _generate_tokens(self, user: User) -> Tuple[str, str]:
        role_id = ""
        if user.role and user.role.id is not None:
            role_id = str(user.role.id)

        access_claims = UserAccessTokenClaims(
            user_id=str(user.id),
            name=user.name,
            role_id=role_id,
        )
        refresh_claims = UserRefreshTokenClaims(user_id=str(user.id))
        return create_access_token(access_claims), create_refresh_token(refresh_claims)

    async def _set_user_online_unless_dnd(self, user: User) -> None:
        if user.state == UserState.DND:
            return
        await self.repo_user.update_user_state_by_id(user.id, UserState.ONLINE)

    def _ensure_user_can_authenticate(self, user: User) -> None:
        if user.status == UserStatus.SUSPENDED:
            raise ForbiddenDomainException("User is suspended.")
        if user.status == UserStatus.BANNED:
            raise ForbiddenDomainException("User is banned.")
