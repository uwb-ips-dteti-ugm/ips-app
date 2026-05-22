from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.user import User, UserAuth, UserStatus
from ips_app.domain.models.permission import Permission


class UserRepository(ABC):
    @abstractmethod
    async def create_user(
        self,
        role_id: Any,
        name: str,
        created_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> User:
        """Create a user without auth records."""
        ...

    @abstractmethod
    async def add_user_auth_by_id(
        self,
        id: Any,
        auth: UserAuth,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Add an embedded auth record to a user."""
        ...

    @abstractmethod
    async def read_user_by_id(self, id: Any, **kwargs: Any) -> User:
        """Read a user by its ID."""
        ...

    @abstractmethod
    async def read_user_by_password_username(
        self,
        username: str,
        **kwargs: Any,
    ) -> User:
        """Read a user by password-auth username."""
        ...

    @abstractmethod
    async def read_users_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        role_id: Optional[Any] = None,
        status: Optional[UserStatus] = None,
        **kwargs: Any,
    ) -> Tuple[List[User], int]:
        """Read users with pagination and filtering."""
        ...

    @abstractmethod
    async def read_user_permissions_by_id(self, id: Any, **kwargs: Any) -> List[Permission]:
        """Read a user's permissions by their ID."""
        ...

    @abstractmethod
    async def update_user_password_auth_by_id(
        self,
        id: Any,
        username: Optional[str] = None,
        password_hash: Optional[str] = None,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Update a user's password-auth profile fields."""
        ...

    @abstractmethod
    async def update_user_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Update user basic info."""
        ...

    @abstractmethod
    async def update_user_status_by_id(
        self,
        id: Any,
        status: UserStatus,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Update user status."""
        ...

    @abstractmethod
    async def update_user_role_by_id(
        self,
        id: Any,
        role_id: Any,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Update user role."""
        ...

    @abstractmethod
    async def update_user_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Update user preferences."""
        ...

    @abstractmethod
    async def delete_user_by_id(self, id: Any, **kwargs: Any) -> None:
        """Delete a user by its ID."""
        ...
