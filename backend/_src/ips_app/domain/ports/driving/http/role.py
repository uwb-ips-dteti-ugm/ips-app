from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.permission import Permission
from ips_app.domain.models.role import Role


class RoleHTTP(ABC):
    @abstractmethod
    async def add_role(
        self,
        name: str,
        description: str = "",
        is_default: bool = False,
        created_by: Optional[Any] = None,
    ) -> Role:
        """Add a new role."""
        ...

    @abstractmethod
    async def get_role(self, role_id: Any) -> Role:
        """Get a role by its ID."""
        ...

    @abstractmethod
    async def get_default_role(self) -> Role:
        """Get the default role."""
        ...

    @abstractmethod
    async def get_roles(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Role], int]:
        """Get roles with cursor-compatible pagination."""
        ...

    @abstractmethod
    async def get_role_permissions(self, role_id: Any) -> List[Permission]:
        """Get permissions bound to a role."""
        ...

    @abstractmethod
    async def set_role(
        self,
        role_id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> Role:
        """Update a role's basic information."""
        ...

    @abstractmethod
    async def set_default_role(
        self,
        role_id: Any,
        updated_by: Optional[Any] = None,
    ) -> Role:
        """Set a role as the default role."""
        ...

    @abstractmethod
    async def set_role_preferences(
        self,
        role_id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> Role:
        """Update a role's preferences."""
        ...

    @abstractmethod
    async def remove_role(self, role_id: Any) -> str:
        """Remove a role if no user uses it."""
        ...

    @abstractmethod
    async def add_permissions_to_role(
        self,
        role_id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
    ) -> Role:
        """Bind permissions to a role."""
        ...

    @abstractmethod
    async def remove_permissions_from_role(
        self,
        role_id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
    ) -> Role:
        """Unbind permissions from a role."""
        ...
