from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Any, Dict
from ips_app.domain.models.role import Role


class RoleRepositoryPort(ABC):
    @abstractmethod
    async def create_role(
        self,
        name: str,
        description: str,
        is_default: bool = False,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> Role:
        """Create a new role."""
        ...

    @abstractmethod
    async def read_role_by_id(self, id: Any, **kwargs: Any) -> Optional[Role]:
        """Read a role by its ID."""
        ...

    @abstractmethod
    async def read_roles_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List[Role], int]:
        """Read roles with pagination and search."""
        ...

    @abstractmethod
    async def read_role_default(self, **kwargs: Any) -> Optional[Role]:
        """Read the default role."""
        ...

    @abstractmethod
    async def update_role_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update role name or description."""
        ...

    @abstractmethod
    async def update_role_is_default_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Set a role as the default role."""
        ...

    @abstractmethod
    async def update_role_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Update role preferences."""
        ...

    @abstractmethod
    async def delete_role_by_id(self, id: Any, **kwargs: Any) -> None:
        """Delete a role by its ID."""
        ...

    @abstractmethod
    async def add_permissions_to_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Add permissions to a role."""
        ...

    @abstractmethod
    async def remove_permissions_from_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Remove permissions from a role."""
        ...
