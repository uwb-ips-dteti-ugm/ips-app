from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.permission import Permission
from ips_app.domain.models.user import User, UserStatus
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.user import UserRepository
from ips_app.domain.ports.driving.http.user import UserHTTP


class BaseUserHTTP(UserHTTP):
    def __init__(
        self,
        repo: UserRepository,
        log: LeveledLogging,
    ):
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def get_user(self, user_id: Any) -> User:
        tag = f"{self.tag_class}.get_user"
        try:
            return await self.repo.read_user_by_id(user_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get user",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_users(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        role_id: Optional[Any] = None,
        status: Optional[UserStatus] = None,
    ) -> Tuple[List[User], int]:
        tag = f"{self.tag_class}.get_users"
        try:
            return await self.repo.read_users_by_pagination(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
                role_id=role_id,
                status=status,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get users",
                {
                    "error": str(e),
                    "page": page,
                    "limit": limit,
                    "status": str(status) if status else None,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_user_permissions(self, user_id: Any) -> List[Permission]:
        tag = f"{self.tag_class}.get_user_permissions"
        try:
            return await self.repo.read_user_permissions_by_id(user_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get user permissions",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_user_info(
        self,
        user_id: Any,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> User:
        tag = f"{self.tag_class}.set_user_info"
        try:
            await self.repo.update_user_by_id(
                id=user_id,
                name=name,
                bio=bio,
                updated_by=updated_by,
            )
            user = await self.get_user(user_id)
            await self.log.info(
                tag,
                "Successfully updated user info",
                {"id": str(user_id)},
            )
            return user
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set user info",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_user_preferences(
        self,
        user_id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> User:
        tag = f"{self.tag_class}.set_user_preferences"
        try:
            await self.repo.update_user_preferences_by_id(
                id=user_id,
                preferences=preferences,
                updated_by=updated_by,
            )
            user = await self.get_user(user_id)
            await self.log.info(
                tag,
                "Successfully updated user preferences",
                {"id": str(user_id)},
            )
            return user
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set user preferences",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_user_role(
        self,
        user_id: Any,
        role_id: Any,
        updated_by: Optional[Any] = None,
    ) -> User:
        tag = f"{self.tag_class}.set_user_role"
        try:
            await self.repo.update_user_role_by_id(
                id=user_id,
                role_id=role_id,
                updated_by=updated_by,
            )
            user = await self.get_user(user_id)
            await self.log.info(
                tag,
                "Successfully updated user role",
                {"id": str(user_id), "role_id": str(role_id)},
            )
            return user
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set user role",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_user_status(
        self,
        user_id: Any,
        status: UserStatus,
        updated_by: Optional[Any] = None,
    ) -> User:
        tag = f"{self.tag_class}.set_user_status"
        try:
            await self.repo.update_user_status_by_id(
                id=user_id,
                status=status,
                updated_by=updated_by,
            )
            user = await self.get_user(user_id)
            await self.log.info(
                tag,
                "Successfully updated user status",
                {"id": str(user_id), "status": str(status)},
            )
            return user
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set user status",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_user(self, user_id: Any) -> str:
        tag = f"{self.tag_class}.remove_user"
        try:
            await self.repo.delete_user_by_id(user_id)
            await self.log.info(
                tag,
                "Successfully removed user",
                {"id": str(user_id)},
            )
            return "User removed successfully"
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove user",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e
