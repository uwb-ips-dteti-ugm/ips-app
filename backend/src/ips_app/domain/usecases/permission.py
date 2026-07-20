from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.permission import Permission


class PermissionUsecase(ABC):
    @abstractmethod
    async def create_permission(
        self,
        name: str,
        description: str = "",
        created_by: Optional[Any] = None,
    ) -> Permission: ...

    @abstractmethod
    async def get_permission_by_id(self, id: Any) -> Permission: ...

    @abstractmethod
    async def get_permission_by_name(self, name: str) -> Permission: ...

    @abstractmethod
    async def permission_exists_by_name(self, name: str) -> bool: ...

    @abstractmethod
    async def get_permissions(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
    ) -> Tuple[List[Permission], int]: ...

    @abstractmethod
    async def update_permission(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> Permission: ...

    @abstractmethod
    async def update_permission_preferences(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> Permission: ...

    @abstractmethod
    async def delete_permission(self, id: Any) -> None: ...
