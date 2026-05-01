from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Any
from ips_app.domain.models.user import User, UserState, UserStatus

class UserHTTPPort(ABC):
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
        role_id: Optional[Any] = None
    ) -> Tuple[List[User], int]:
        """Get a list of users with pagination and filtering."""
        ...

    @abstractmethod
    async def set_user_info(
        self, 
        user_id: Any, 
        name: Optional[str] = None, 
        bio: Optional[str] = None
    ) -> User:
        """Update a user's basic information."""
        ...

    @abstractmethod
    async def set_user_preferences(self, user_id: Any, preferences: bytes) -> User:
        """Update a user's preferences."""
        ...

    @abstractmethod
    async def set_user_role(self, user_id: Any, role_id: Any) -> User:
        """Update a user's role."""
        ...

    @abstractmethod
    async def set_user_state(self, user_id: Any, state: UserState) -> User:
        """Update a user's state."""
        ...

    @abstractmethod
    async def set_user_status(self, user_id: Any, status: UserStatus) -> User:
        """Update a user's status."""
        ...

    @abstractmethod
    async def remove_user(self, user_id: Any) -> str:
        """Remove a user."""
        ...
