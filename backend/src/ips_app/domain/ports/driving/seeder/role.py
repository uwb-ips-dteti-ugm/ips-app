from abc import ABC, abstractmethod
from typing import List, Optional

from ips_app.domain.models.role import Role


class RoleSeeder(ABC):
    @abstractmethod
    async def role_exists(self, name: str) -> bool:
        """Check whether a role with this name already exists."""
        ...

    @abstractmethod
    async def add_role(
        self,
        name: str,
        description: str = "",
        is_default: bool = False,
        permission_names: Optional[List[str]] = None,
    ) -> Role:
        """Add a seeded role and its initial permission links."""
        ...
