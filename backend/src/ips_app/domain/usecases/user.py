from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.permission import Permission
from ips_app.domain.models.user import User, UserStatus


class UserUsecase(ABC):
    @abstractmethod
    async def create_user(
        self,
        role_id: Any,
        name: str,
        username: str,
        password: str,
        bio: str = "",
        created_by: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def get_user_by_id(self, id: Any) -> User: ...

    @abstractmethod
    async def get_user_by_username(self, username: str) -> User: ...

    @abstractmethod
    async def user_exists_by_username(self, username: str) -> bool: ...

    @abstractmethod
    async def get_users(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        role_id: Optional[Any] = None,
        status: Optional[UserStatus] = None,
    ) -> Tuple[List[User], int]: ...

    @abstractmethod
    async def get_user_permissions(self, id: Any) -> List[Permission]: ...

    @abstractmethod
    async def update_user_info(
        self,
        id: Any,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        username: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def update_user_preferences(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def update_user_role(
        self,
        id: Any,
        role_id: Any,
        updated_by: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def update_user_status(
        self,
        id: Any,
        status: UserStatus,
        updated_by: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def delete_user(self, id: Any) -> None: ...
