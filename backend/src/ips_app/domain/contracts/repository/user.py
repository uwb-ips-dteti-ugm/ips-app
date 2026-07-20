from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.permission import Permission
from ips_app.domain.models.user import User, UserStatus


class UserRepository(ABC):
    @abstractmethod
    async def create_user(
        self,
        role_id: Any,
        name: str,
        username: str,
        password_hash: str,
        bio: str = "",
        created_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def read_user_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def read_user_by_username(
        self,
        username: str,
        session: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def read_users_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        role_id: Optional[Any] = None,
        status: Optional[UserStatus] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[User], int]: ...

    @abstractmethod
    async def read_user_permissions_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> List[Permission]: ...

    @abstractmethod
    async def update_user_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        username: Optional[str] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def update_user_password_by_id(
        self,
        id: Any,
        password_hash: str,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def update_user_status_by_id(
        self,
        id: Any,
        status: UserStatus,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def update_user_role_by_id(
        self,
        id: Any,
        role_id: Any,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def update_user_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User: ...

    @abstractmethod
    async def delete_user_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> None: ...
