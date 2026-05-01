from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Any, Dict
from ips_app.domain.models.role import Role
from ips_app.domain.models.permission import Permission

class RoleRepositoryPort(ABC):
    @abstractmethod
    async def create_role(
        self, 
        name: str, 
        description: str, 
        is_default: bool = False, 
        created_by: Optional[int] = None
    ) -> Role:
        """Create a new role."""
        ...

    @abstractmethod
    async def read_role_by_id(self, id: Any) -> Optional[Role]:
        """Read a role by its ID."""
        ...

    @abstractmethod
    async def read_roles_by_pagination(
        self, 
        page: int, 
        limit: int, 
        cursor_id: Optional[Any] = None, 
        search: Optional[str] = None
    ) -> Tuple[List[Role], int]:
        """Read roles with pagination and search."""
        ...

    @abstractmethod
    async def read_role_default(self) -> Optional[Role]:
        """Read the default role."""
        ...

    @abstractmethod
    async def update_role_by_id(
        self, 
        id: Any, 
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        updated_by: Optional[int] = None
    ) -> None:
        """Update role name or description."""
        ...

    @abstractmethod
    async def update_role_is_default_by_id(self, id: Any, updated_by: Optional[int] = None) -> None:
        """Set a role as the default role."""
        ...

    @abstractmethod
    async def update_role_preferences_by_id(
        self, 
        id: Any, 
        preferences: Dict[str, Any], 
        updated_by: Optional[int] = None
    ) -> None:
        """Update role preferences."""
        ...

    @abstractmethod
    async def delete_role_by_id(self, id: Any) -> None:
        """Delete a role by its ID."""
        ...
        
    # Helper methods for role-permission management
    @abstractmethod
    async def add_permissions_to_role(self, id: Any, permission_ids: List[Any], updated_by: Optional[int] = None) -> None:
        """Add permissions to a role."""
        ...
        
    @abstractmethod
    async def remove_permissions_from_role(self, id: Any, permission_ids: List[Any], updated_by: Optional[int] = None) -> None:
        """Remove permissions from a role."""
        ...
