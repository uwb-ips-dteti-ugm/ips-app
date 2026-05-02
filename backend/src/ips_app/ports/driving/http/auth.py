from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any

class AuthHTTPPort(ABC):
    @abstractmethod
    async def sign_up(
        self, 
        name: str, 
        username: str, 
        password: str
    ) -> Tuple[str, str]:
        """Sign up a new user and return (access_token, refresh_token)."""
        ...

    @abstractmethod
    async def register(
        self,
        name: str,
        username: str,
        password: str,
        role_id: Any
    ) -> Any:
        """Register a new user from the admin panel."""
        ...

    @abstractmethod
    async def sign_in(
        self, 
        sign_in_identifier: str, 
        password: str
    ) -> Tuple[str, str]:
        """Sign in a user and return (access_token, refresh_token)."""
        ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh the access token and return (new_access_token, new_refresh_token)."""
        ...

    @abstractmethod
    async def sign_out(self, user_id: Any) -> None:
        """Sign out a user."""
        ...

    @abstractmethod
    async def set_new_password(self, user_id: Any, new_password: str) -> None:
        """Force-set a new password without verification. Admin/super-admin operation."""
        ...

    @abstractmethod
    async def set_new_password_with_old_password(
        self,
        user_id: Any,
        old_password: str,
        new_password: str
    ) -> None:
        """Update password by verifying the old one."""
        ...

    @abstractmethod
    async def set_auth_info(
        self,
        user_id: Any,
        username: Optional[str] = None
    ) -> None:
        """Update auth basic information."""
        ...
