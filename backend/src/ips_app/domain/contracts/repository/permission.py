from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.permission import Permission


class PermissionRepository(ABC):
    @abstractmethod
    async def create_permission(
        self,
        name: str,
        description: str = "",
        created_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Permission: ...

    @abstractmethod
    async def read_permission_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> Permission: ...

    @abstractmethod
    async def read_permission_by_name(
        self,
        name: str,
        session: Optional[Any] = None,
    ) -> Permission: ...

    @abstractmethod
    async def read_permissions_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[Permission], int]: ...

    @abstractmethod
    async def update_permission_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Permission: ...

    @abstractmethod
    async def update_permission_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Permission: ...

    @abstractmethod
    async def delete_permission_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> None: ...
