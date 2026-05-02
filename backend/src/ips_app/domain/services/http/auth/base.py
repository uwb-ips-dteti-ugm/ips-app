from typing import Optional, Tuple, Any
from motor.motor_asyncio import AsyncIOMotorClient
from ips_app.domain.models.user import User, UserState, UserAccessTokenClaims, UserRefreshTokenClaims
from ips_app.ports.driving.http.auth import AuthHTTPPort
from ips_app.ports.driven.repository.auth import AuthRepositoryPort
from ips_app.ports.driven.repository.user import UserRepositoryPort
from ips_app.ports.driven.repository.role import RoleRepositoryPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.domain.models.exception import DomainException, NotFoundException
from ips_app.utils.password import hash_password, verify_password
from ips_app.utils.token import create_access_token, create_refresh_token, validate_refresh_token


class AuthHTTPService(AuthHTTPPort):
    def __init__(
        self,
        motor_client: AsyncIOMotorClient,
        repo_auth: AuthRepositoryPort,
        repo_user: UserRepositoryPort,
        repo_role: RoleRepositoryPort,
        log: GenericLoggingPort,
    ):
        self.motor_client = motor_client
        self.repo_auth = repo_auth
        self.repo_user = repo_user
        self.repo_role = repo_role
        self.log = log
        self.tag_class = "AuthHTTPService"

    def _make_tokens(self, user: User, role_id: Any) -> Tuple[str, str]:
        access_claims = UserAccessTokenClaims(
            user_id=str(user.id),
            name=user.name,
            role_id=str(role_id),
        )
        refresh_claims = UserRefreshTokenClaims(user_id=str(user.id))
        return create_access_token(access_claims), create_refresh_token(refresh_claims)

    async def sign_up(self, name: str, username: str, password: str) -> Tuple[str, str]:
        tag = f"{self.tag_class}.sign_up"
        try:
            default_role = await self.repo_role.read_role_default()
            if not default_role:
                raise NotFoundException("default", "roles")

            async with await self.motor_client.start_session() as session:
                async with session.start_transaction():
                    user = await self.repo_user.create_user(
                        role_id=default_role.id, name=name, session=session
                    )
                    await self.repo_auth.create_auth(
                        user_id=user.id,
                        username=username,
                        password_hash=hash_password(password),
                        session=session,
                    )

            await self.log.info(tag, "Successfully signed up user", {"user_id": str(user.id), "username": username})
            return self._make_tokens(user, default_role.id)
        except Exception as e:
            await self.log.error(tag, "Failed to sign up", {"error": str(e), "username": username})
            raise e

    async def register(self, name: str, username: str, password: str, role_id: Any) -> User:
        tag = f"{self.tag_class}.register"
        try:
            async with await self.motor_client.start_session() as session:
                async with session.start_transaction():
                    user = await self.repo_user.create_user(
                        role_id=role_id, name=name, session=session
                    )
                    await self.repo_auth.create_auth(
                        user_id=user.id,
                        username=username,
                        password_hash=hash_password(password),
                        session=session,
                    )

            await self.log.info(tag, "Successfully registered user", {"user_id": str(user.id), "username": username})
            return user
        except Exception as e:
            await self.log.error(tag, "Failed to register user", {"error": str(e), "username": username})
            raise e

    async def sign_in(self, sign_in_identifier: str, password: str) -> Tuple[str, str]:
        tag = f"{self.tag_class}.sign_in"
        try:
            auth = await self.repo_auth.read_auth_by_sign_in_identifier(sign_in_identifier)
            if not auth or not verify_password(password, auth.password_hash):
                raise DomainException("Invalid credentials.")

            await self.repo_user.update_user_last_signed_in_at_by_id(auth.user.id)
            await self.log.info(tag, "Successfully signed in user", {"username": sign_in_identifier})
            return self._make_tokens(auth.user, auth.user.role.id)
        except Exception as e:
            await self.log.error(tag, "Failed to sign in", {"error": str(e), "identifier": sign_in_identifier})
            raise e

    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        tag = f"{self.tag_class}.refresh_token"
        try:
            claims = validate_refresh_token(refresh_token)
            user = await self.repo_user.read_user_by_id(claims.user_id)
            if not user:
                raise NotFoundException(claims.user_id, "users")

            await self.repo_user.update_user_last_refreshed_at_by_id(user.id)
            await self.log.info(tag, "Successfully refreshed token", {"user_id": claims.user_id})
            return self._make_tokens(user, user.role.id)
        except Exception as e:
            await self.log.error(tag, "Failed to refresh token", {"error": str(e)})
            raise e

    async def sign_out(self, user_id: Any) -> None:
        tag = f"{self.tag_class}.sign_out"
        try:
            await self.repo_user.update_user_state_by_id(user_id, UserState.OFFLINE)
            await self.log.info(tag, "Successfully signed out user", {"user_id": str(user_id)})
        except Exception as e:
            await self.log.error(tag, "Failed to sign out", {"error": str(e), "user_id": str(user_id)})
            raise e

    async def set_new_password(self, user_id: Any, new_password: str) -> None:
        tag = f"{self.tag_class}.set_new_password"
        try:
            auth = await self.repo_auth.read_auth_by_user_id(user_id)
            if not auth:
                raise NotFoundException(str(user_id), "auths")
            await self.repo_auth.update_auth_password_by_id(auth.id, hash_password(new_password))
            await self.log.info(tag, "Successfully force-set password", {"user_id": str(user_id)})
        except Exception as e:
            await self.log.error(tag, "Failed to force-set password", {"error": str(e), "user_id": str(user_id)})
            raise e

    async def set_new_password_with_old_password(
        self,
        user_id: Any,
        old_password: str,
        new_password: str,
    ) -> None:
        tag = f"{self.tag_class}.set_new_password_with_old_password"
        try:
            auth = await self.repo_auth.read_auth_by_user_id(user_id)
            if not auth or not verify_password(old_password, auth.password_hash):
                raise DomainException("Invalid credentials.")

            await self.repo_auth.update_auth_password_by_id(auth.id, hash_password(new_password))
            await self.log.info(tag, "Successfully updated password", {"user_id": str(user_id)})
        except Exception as e:
            await self.log.error(tag, "Failed to update password", {"error": str(e), "user_id": str(user_id)})
            raise e

    async def set_auth_info(
        self,
        user_id: Any,
        username: Optional[str] = None
    ) -> None:
        tag = f"{self.tag_class}.set_auth_info"
        try:
            auth = await self.repo_auth.read_auth_by_user_id(user_id)
            if not auth:
                raise NotFoundException(str(user_id), "auths")

            await self.repo_auth.update_auth_info_by_id(auth.id, username)
            await self.log.info(tag, "Successfully updated auth info", {"user_id": str(user_id)})
        except Exception as e:
            await self.log.error(tag, "Failed to update auth info", {"error": str(e), "user_id": str(user_id)})
            raise e

