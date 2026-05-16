from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.user import User, UserAuth, UserAuthType, UserState, UserStatus


class UserRepository(ABC):
    @abstractmethod
    async def create_user(
        self,
        role_id: Any,
        name: str,
        auths: Optional[List[UserAuth]] = None,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> User:
        """Create a user, optionally with embedded auth records."""
        ...

    @abstractmethod
    async def read_user_by_id(self, id: Any, **kwargs: Any) -> User:
        """Read a user by its ID."""
        ...

    @abstractmethod
    async def read_user_by_username(
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
        state: Optional[UserState] = None,
        status: Optional[UserStatus] = None,
        **kwargs: Any,
    ) -> Tuple[List[User], int]:
        """Read users with pagination and filtering."""
        ...

    @abstractmethod
    async def add_user_auth_by_id(
        self,
        id: Any,
        auth: UserAuth,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Add an embedded auth record to a user."""
        ...

    @abstractmethod
    async def update_user_password_auth_info_by_id(
        self,
        id: Any,
        username: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update a user's password-auth profile fields."""
        ...

    @abstractmethod
    async def update_user_password_auth_password_by_id(
        self,
        id: Any,
        password_hash: str,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update a user's password-auth password hash."""
        ...

    @abstractmethod
    async def delete_user_auth_by_id(
        self,
        id: Any,
        auth_type: UserAuthType,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Delete a user's embedded auth record by auth type."""
        ...

    @abstractmethod
    async def update_user_info_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update user basic info."""
        ...

    @abstractmethod
    async def update_user_state_by_id(
        self,
        id: Any,
        state: UserState,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update user state."""
        ...

    @abstractmethod
    async def update_user_status_by_id(
        self,
        id: Any,
        status: UserStatus,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update user status."""
        ...

    @abstractmethod
    async def update_user_role_by_id(
        self,
        id: Any,
        role_id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update user role."""
        ...

    @abstractmethod
    async def update_user_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update user preferences."""
        ...

    @abstractmethod
    async def update_user_last_signed_in_at_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update user last signed-in timestamp."""
        ...

    @abstractmethod
    async def update_user_last_refreshed_at_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update user last refreshed timestamp."""
        ...

    @abstractmethod
    async def update_user_last_activity_at_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update user last activity timestamp."""
        ...

    @abstractmethod
    async def update_users_state_with_cutoffs(
        self,
        away_cutoff: datetime,
        offline_cutoff: datetime,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> Tuple[int, int]:
        """Update users' state and return away/offline modified counts."""
        ...

    @abstractmethod
    async def delete_user_by_id(self, id: Any, **kwargs: Any) -> None:
        """Delete a user by its ID."""
        ...
