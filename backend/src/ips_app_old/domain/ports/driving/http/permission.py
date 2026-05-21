from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from ips_app_old.domain.models.permission import Permission


class PermissionHTTP(ABC):
    @abstractmethod
    async def add_permission(self, name: str, description: str) -> Permission:
        """Add a new permission."""
        ...

    @abstractmethod
    async def get_permission(self, permission_id: Any) -> Permission:
        """Get a permission by its ID."""
        ...

    @abstractmethod
    async def get_permissions(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Permission], int]:
        """Get permissions with pagination."""
        ...

    @abstractmethod
    async def set_permission(
        self,
        permission_id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Permission:
        """Update a permission's basic information."""
        ...

    @abstractmethod
    async def set_permission_preferences(
        self,
        permission_id: Any,
        preferences: bytes,
    ) -> Permission:
        """Update a permission's preferences."""
        ...

    @abstractmethod
    async def remove_permission(self, permission_id: Any) -> str:
        """Remove a permission."""
        ...
