from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Any
from ips_app.domain.models.auth import Auth


class AuthRepositoryPort(ABC):
    @abstractmethod
    async def create_auth(
        self,
        user_id: Any,
        username: str,
        password_hash: str,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> Auth:
        """Create a new auth record."""
        ...

    @abstractmethod
    async def read_auths_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List[Auth], int]:
        """Read auths with pagination and search."""
        ...

    @abstractmethod
    async def read_auth_by_id(self, id: Any, **kwargs: Any) -> Optional[Auth]:
        """Read an auth record by its ID."""
        ...

    @abstractmethod
    async def read_auth_by_user_id(self, user_id: Any, **kwargs: Any) -> Optional[Auth]:
        """Read an auth record by user ID."""
        ...

    @abstractmethod
    async def read_auth_by_sign_in_identifier(
        self,
        sign_in_identifier: str,
        **kwargs: Any,
    ) -> Optional[Auth]:
        """Read an auth record by username."""
        ...

    @abstractmethod
    async def update_auth_info_by_id(
        self,
        id: Any,
        username: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update auth basic info."""
        ...

    @abstractmethod
    async def update_auth_password_by_id(
        self,
        id: Any,
        password_hash: str,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update auth password."""
        ...

    @abstractmethod
    async def delete_auth_by_user_id(self, user_id: Any, **kwargs: Any) -> None:
        """Delete an auth record by user ID."""
        ...
