from abc import ABC, abstractmethod

from ips_app.domain.models.permission import Permission


class PermissionSeeder(ABC):
    @abstractmethod
    async def permission_exists(self, name: str) -> bool:
        """Check whether a permission with this name already exists."""
        ...

    @abstractmethod
    async def add_permission(
        self,
        name: str,
        description: str = "",
    ) -> Permission:
        """Add a seeded permission."""
        ...
