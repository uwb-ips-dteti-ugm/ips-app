from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from ips_app.domain.models.user import User


class AuthHTTP(ABC):
    @abstractmethod
    async def sign_up(
        self,
        name: str,
        username: str,
        password: str,
    ) -> Tuple[str, str]:
        """Sign up a new user and return access and refresh tokens."""
        ...

    @abstractmethod
    async def register(
        self,
        name: str,
        username: str,
        password: str,
        role_id: Any,
    ) -> User:
        """Register a new user from the admin panel."""
        ...

    @abstractmethod
    async def sign_in(
        self,
        sign_in_identifier: str,
        password: str,
    ) -> Tuple[str, str]:
        """Sign in a user and return access and refresh tokens."""
        ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh tokens and return a new access and refresh token pair."""
        ...

    @abstractmethod
    async def sign_out(self, user_id: Any) -> None:
        """Sign out a user."""
        ...

    @abstractmethod
    async def set_new_password(self, user_id: Any, new_password: str) -> None:
        """Force-set a new password by user identity."""
        ...

    @abstractmethod
    async def set_new_password_with_old_password(
        self,
        user_id: Any,
        old_password: str,
        new_password: str,
    ) -> None:
        """Update a password after verifying the old password."""
        ...

    @abstractmethod
    async def set_auth_info(self, user_id: Any, username: Optional[str] = None) -> None:
        """Update embedded auth information by user identity."""
        ...

    @abstractmethod
    async def get_auths_users(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        """Get users with embedded auth data for auth management."""
        ...
