from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Tuple, Any, Dict
from ips_app.domain.models.user import User, UserState, UserStatus

class UserRepositoryPort(ABC):
    @abstractmethod
    async def create_user(
        self, 
        role_id: Any, 
        name: str, 
        created_by: Optional[int] = None
    ) -> User:
        """Create a new user."""
        ...

    @abstractmethod
    async def read_user_by_id(self, id: Any) -> Optional[User]:
        """Read a user by its ID."""
        ...

    @abstractmethod
    async def read_users_by_pagination(
        self, 
        page: int, 
        limit: int, 
        cursor_id: Optional[Any] = None, 
        search: Optional[str] = None, 
        role_id: Optional[Any] = None
    ) -> Tuple[List[User], int]:
        """Read users with pagination and filtering."""
        ...

    @abstractmethod
    async def update_user_info_by_id(
        self, 
        id: Any, 
        name: Optional[str] = None, 
        bio: Optional[str] = None, 
        updated_by: Optional[int] = None
    ) -> None:
        """Update user basic info."""
        ...

    @abstractmethod
    async def update_user_state_by_id(self, id: Any, state: UserState, updated_by: Optional[int] = None) -> None:
        """Update user state (online, offline, etc.)."""
        ...

    @abstractmethod
    async def update_user_status_by_id(self, id: Any, status: UserStatus, updated_by: Optional[int] = None) -> None:
        """Update user status (active, suspended, etc.)."""
        ...

    @abstractmethod
    async def update_user_role_by_id(self, id: Any, role_id: Any, updated_by: Optional[int] = None) -> None:
        """Update user role."""
        ...

    @abstractmethod
    async def update_user_preferences_by_id(
        self, 
        id: Any, 
        preferences: Dict[str, Any], 
        updated_by: Optional[int] = None
    ) -> None:
        """Update user preferences."""
        ...

    @abstractmethod
    async def update_user_last_signed_in_at_by_id(self, id: Any, updated_by: Optional[int] = None) -> None:
        """Update user last signed in timestamp."""
        ...

    @abstractmethod
    async def update_user_last_refreshed_at_by_id(self, id: Any, updated_by: Optional[int] = None) -> None:
        """Update user last refreshed timestamp."""
        ...

    @abstractmethod
    async def update_user_last_activity_at_by_id(self, id: Any, updated_by: Optional[int] = None) -> None:
        """Update user last activity timestamp."""
        ...

    @abstractmethod
    async def delete_user_by_id(self, id: Any) -> None:
        """Delete a user by its ID."""
        ...
