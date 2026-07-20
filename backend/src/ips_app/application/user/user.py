from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.repository.user import UserRepository
from ips_app.domain.contracts.utility.password import PasswordHasher
from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.permission import Permission
from ips_app.domain.models.user import User, UserStatus
from ips_app.domain.usecases.user import UserUsecase

from ips_app.application._shared.validator import (
    validate_bio,
    validate_name,
    validate_password,
    validate_username,
)


class BaseUserUsecase(UserUsecase):
    def __init__(
        self,
        repo: UserRepository,
        password_hasher: PasswordHasher,
        log: LeveledLogger,
    ) -> None:
        self.repo = repo
        self.password_hasher = password_hasher
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_user(
        self,
        role_id: Any,
        name: str,
        username: str,
        password: str,
        bio: str = "",
        created_by: Optional[Any] = None,
    ) -> User:
        tag = f"{self.tag_class}/create_user"
        try:
            validate_name(name)
            validate_username(username)
            validate_password(password)
            validate_bio(bio)
            password_hash = self.password_hasher.hash(password)
            user = await self.repo.create_user(
                role_id=role_id,
                name=name,
                username=username,
                password_hash=password_hash,
                bio=bio,
                created_by=created_by,
            )
            await self.log.info(
                tag,
                "Successfully created user",
                {"id": str(user.id), "username": username},
            )
            return user
        except Exception as e:
            await self.log.error(
                tag, "Failed to create user", {"error": str(e), "username": username}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_user_by_id(self, id: Any) -> User:
        tag = f"{self.tag_class}/get_user_by_id"
        try:
            user = await self.repo.read_user_by_id(id)
            await self.log.info(tag, "Successfully retrieved user", {"id": str(id)})
            return user
        except Exception as e:
            await self.log.error(
                tag, "Failed to retrieve user", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_user_by_username(self, username: str) -> User:
        tag = f"{self.tag_class}/get_user_by_username"
        try:
            user = await self.repo.read_user_by_username(username)
            await self.log.info(
                tag, "Successfully retrieved user", {"username": username}
            )
            return user
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve user",
                {"error": str(e), "username": username},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def user_exists_by_username(self, username: str) -> bool:
        tag = f"{self.tag_class}/user_exists_by_username"
        try:
            exists = True
            try:
                await self.repo.read_user_by_username(username)
            except NotFoundDomainException:
                exists = False
            await self.log.info(
                tag,
                "Successfully checked user existence",
                {"username": username, "exists": exists},
            )
            return exists
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to check user existence",
                {"error": str(e), "username": username},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_users(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        role_id: Optional[Any] = None,
        status: Optional[UserStatus] = None,
    ) -> Tuple[List[User], int]:
        tag = f"{self.tag_class}/get_users"
        try:
            users, total = await self.repo.read_users_by_pagination(
                page=page,
                limit=limit,
                search=search,
                role_id=role_id,
                status=status,
            )
            await self.log.info(
                tag,
                "Successfully retrieved users",
                {"page": page, "limit": limit, "total": total},
            )
            return users, total
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve users",
                {"error": str(e), "page": page, "limit": limit},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_user_permissions(self, id: Any) -> List[Permission]:
        tag = f"{self.tag_class}/get_user_permissions"
        try:
            permissions = await self.repo.read_user_permissions_by_id(id)
            await self.log.info(
                tag, "Successfully retrieved user permissions", {"id": str(id)}
            )
            return permissions
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve user permissions",
                {"error": str(e), "id": str(id)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_info(
        self,
        id: Any,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        username: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> User:
        tag = f"{self.tag_class}/update_user_info"
        try:
            if name is not None:
                validate_name(name)
            if bio is not None:
                validate_bio(bio)
            if username is not None:
                validate_username(username)
            user = await self.repo.update_user_by_id(
                id=id,
                name=name,
                bio=bio,
                username=username,
                updated_by=updated_by,
            )
            await self.log.info(
                tag, "Successfully updated user info", {"id": str(id)}
            )
            return user
        except Exception as e:
            await self.log.error(
                tag, "Failed to update user info", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_preferences(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> User:
        tag = f"{self.tag_class}/update_user_preferences"
        try:
            user = await self.repo.update_user_preferences_by_id(
                id=id,
                preferences=preferences,
                updated_by=updated_by,
            )
            await self.log.info(
                tag, "Successfully updated user preferences", {"id": str(id)}
            )
            return user
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user preferences",
                {"error": str(e), "id": str(id)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_role(
        self,
        id: Any,
        role_id: Any,
        updated_by: Optional[Any] = None,
    ) -> User:
        tag = f"{self.tag_class}/update_user_role"
        try:
            user = await self.repo.update_user_role_by_id(
                id=id,
                role_id=role_id,
                updated_by=updated_by,
            )
            await self.log.info(
                tag,
                "Successfully updated user role",
                {"id": str(id), "role_id": str(role_id)},
            )
            return user
        except Exception as e:
            await self.log.error(
                tag, "Failed to update user role", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_status(
        self,
        id: Any,
        status: UserStatus,
        updated_by: Optional[Any] = None,
    ) -> User:
        tag = f"{self.tag_class}/update_user_status"
        try:
            user = await self.repo.update_user_status_by_id(
                id=id,
                status=status,
                updated_by=updated_by,
            )
            await self.log.info(
                tag,
                "Successfully updated user status",
                {"id": str(id), "status": str(status)},
            )
            return user
        except Exception as e:
            await self.log.error(
                tag, "Failed to update user status", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def delete_user(self, id: Any) -> None:
        tag = f"{self.tag_class}/delete_user"
        try:
            await self.repo.delete_user_by_id(id)
            await self.log.info(tag, "Successfully deleted user", {"id": str(id)})
        except Exception as e:
            await self.log.error(
                tag, "Failed to delete user", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e
