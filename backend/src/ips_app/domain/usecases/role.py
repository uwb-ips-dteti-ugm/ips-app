from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.permission import Permission
from ips_app.domain.models.role import Role


class RoleUsecase(ABC):
    @abstractmethod
    async def create_role(
        self,
        name: str,
        description: str = "",
        is_default: bool = False,
        created_by: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def get_role_by_id(self, id: Any) -> Role: ...

    @abstractmethod
    async def get_role_by_name(self, name: str) -> Role: ...

    @abstractmethod
    async def role_exists_by_name(self, name: str) -> bool: ...

    @abstractmethod
    async def get_default_role(self) -> Role: ...

    @abstractmethod
    async def get_roles(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
    ) -> Tuple[List[Role], int]: ...

    @abstractmethod
    async def get_role_permissions(self, id: Any) -> List[Permission]: ...

    @abstractmethod
    async def update_role(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def set_default_role(
        self,
        id: Any,
        updated_by: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def update_role_preferences(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def delete_role(self, id: Any) -> None: ...

    @abstractmethod
    async def add_permissions_to_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
    ) -> Role: ...

    @abstractmethod
    async def remove_permissions_from_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
    ) -> Role: ...
