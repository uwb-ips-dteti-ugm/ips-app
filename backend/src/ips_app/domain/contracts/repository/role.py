from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.permission import Permission
from ips_app.domain.models.role import Role


class RoleRepository(ABC):
    @abstractmethod
    async def create_role(
        self,
        name: str,
        description: str = "",
        is_default: bool = False,
        created_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def read_role_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def read_role_by_name(
        self,
        name: str,
        session: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def read_roles_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[Role], int]: ...

    @abstractmethod
    async def read_role_default(
        self,
        session: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def read_role_permissions_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> List[Permission]: ...

    @abstractmethod
    async def update_role_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def update_role_is_default_by_id(
        self,
        id: Any,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def update_role_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def delete_role_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> None: ...

    @abstractmethod
    async def add_permissions_to_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def remove_permissions_from_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role: ...
