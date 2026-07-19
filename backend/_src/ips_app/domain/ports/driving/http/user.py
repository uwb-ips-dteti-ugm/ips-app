from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.permission import Permission
from ips_app.domain.models.user import User, UserStatus


class UserHTTP(ABC):
    @abstractmethod
    async def get_user(self, user_id: Any) -> User:
        """Get a user by its ID."""
        ...

    @abstractmethod
    async def get_users(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        role_id: Optional[Any] = None,
        status: Optional[UserStatus] = None,
    ) -> Tuple[List[User], int]:
        """Get users with cursor-compatible pagination and filtering."""
        ...

    @abstractmethod
    async def get_user_permissions(self, user_id: Any) -> List[Permission]:
        """Get permissions granted to a user through their role."""
        ...

    @abstractmethod
    async def set_user_info(
        self,
        user_id: Any,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> User:
        """Update a user's basic information."""
        ...

    @abstractmethod
    async def set_user_preferences(
        self,
        user_id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> User:
        """Update a user's preferences."""
        ...

    @abstractmethod
    async def set_user_role(
        self,
        user_id: Any,
        role_id: Any,
        updated_by: Optional[Any] = None,
    ) -> User:
        """Update a user's role."""
        ...

    @abstractmethod
    async def set_user_status(
        self,
        user_id: Any,
        status: UserStatus,
        updated_by: Optional[Any] = None,
    ) -> User:
        """Update a user's status."""
        ...

    @abstractmethod
    async def remove_user(self, user_id: Any) -> str:
        """Remove a user."""
        ...
