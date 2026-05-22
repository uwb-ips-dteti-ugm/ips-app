from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from ips_app.domain.models.user import User


class AuthHTTP(ABC):
    @abstractmethod
    async def register(
        self,
        name: str,
        username: str,
        password: str,
        role_id: Any,
        created_by: Optional[Any] = None,
    ) -> User:
        """Register a new user with password auth from an admin workflow."""
        ...

    @abstractmethod
    async def sign_in(
        self,
        username: str,
        password: str,
    ) -> Tuple[str, str]:
        """Sign in with password auth and return access and refresh tokens."""
        ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh tokens and return a new access and refresh token pair."""
        ...

    @abstractmethod
    async def set_password_auth(
        self,
        user_id: Any,
        username: Optional[str] = None,
        password: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> None:
        """Update password-auth username or password by user identity."""
        ...

    @abstractmethod
    async def set_password_with_old_password(
        self,
        user_id: Any,
        old_password: str,
        new_password: str,
        updated_by: Optional[Any] = None,
    ) -> None:
        """Update a password after verifying the old password."""
        ...
