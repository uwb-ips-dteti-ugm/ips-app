from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Any, Dict
from ips_app.domain.models.permission import Permission


class PermissionRepository(ABC):
    @abstractmethod
    async def create_permission(
        self,
        name: str,
        description: str,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> Permission:
        """Create a new permission."""
        ...

    @abstractmethod
    async def read_permission_by_id(self, id: Any, **kwargs: Any) -> Permission:
        """Read a permission by its ID."""
        ...

    @abstractmethod
    async def read_permission_by_name(self, name: str, **kwargs: Any) -> Permission:
        """Read a permission by its name."""
        ...

    @abstractmethod
    async def read_permissions_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List[Permission], int]:
        """Read permissions with pagination and search."""
        ...

    @abstractmethod
    async def update_permission_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update permission name or description."""
        ...

    @abstractmethod
    async def update_permission_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update permission preferences."""
        ...

    @abstractmethod
    async def delete_permission_by_id(self, id: Any, **kwargs: Any) -> None:
        """Delete a permission by its ID."""
        ...
