from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Any
from ips_app.domain.models.role import Role
from ips_app.domain.models.permission import Permission

class RoleHTTPPort(ABC):
    @abstractmethod
    async def add_role(self, name: str, description: str) -> Role:
        """Add a new role."""
        ...

    @abstractmethod
    async def get_role(self, role_id: Any) -> Role:
        """Get a role by its ID."""
        ...

    @abstractmethod
    async def get_roles(
        self, 
        page: int, 
        limit: int, 
        cursor_id: Optional[Any] = None, 
        search: Optional[str] = None
    ) -> Tuple[List[Role], int]:
        """Get a list of roles with pagination."""
        ...

    @abstractmethod
    async def set_role(
        self, 
        role_id: Any, 
        name: Optional[str] = None, 
        description: Optional[str] = None
    ) -> Role:
        """Update a role's basic information."""
        ...

    @abstractmethod
    async def set_role_preferences(self, role_id: Any, preferences: bytes) -> Role:
        """Update a role's preferences."""
        ...

    @abstractmethod
    async def remove_role(self, role_id: Any) -> str:
        """Remove a role."""
        ...

    @abstractmethod
    async def add_permissions_to_role(self, role_id: Any, permission_ids: List[Any]) -> Role:
        """Bind permissions to a role."""
        ...

    @abstractmethod
    async def remove_permissions_from_role(self, role_id: Any, permission_ids: List[Any]) -> Role:
        """Unbind permissions from a role."""
        ...

    @abstractmethod
    async def get_role_permissions(self, role_id: Any) -> List[Permission]:
        """Get permissions bound to a role."""
        ...
