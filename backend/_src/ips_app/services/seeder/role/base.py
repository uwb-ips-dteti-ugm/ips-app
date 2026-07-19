from typing import Any, List, Optional

from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.role import Role
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.permission import PermissionRepository
from ips_app.domain.ports.driven.repository.role import RoleRepository
from ips_app.domain.ports.driving.seeder.role import RoleSeeder


class BaseRoleSeeder(RoleSeeder):
    def __init__(
        self,
        repo_role: RoleRepository,
        repo_permission: PermissionRepository,
        log: LeveledLogging,
    ):
        self.repo_role = repo_role
        self.repo_permission = repo_permission
        self.log = log
        self.tag_class = self.__class__.__name__

    async def role_exists(self, name: str) -> bool:
        tag = f"{self.tag_class}.role_exists"
        try:
            await self.repo_role.read_role_by_name(name)
            return True
        except NotFoundDomainException:
            return False
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to check role existence",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def add_role(
        self,
        name: str,
        description: str = "",
        is_default: bool = False,
        permission_names: Optional[List[str]] = None,
    ) -> Role:
        tag = f"{self.tag_class}.add_role"
        try:
            permission_ids: List[Any] = []
            for permission_name in permission_names or []:
                permission = await self.repo_permission.read_permission_by_name(
                    permission_name,
                )
                permission_ids.append(permission.id)

            role = await self.repo_role.create_role(
                name=name,
                description=description,
                is_default=is_default,
            )
            if permission_ids:
                await self.repo_role.add_permissions_to_role(
                    id=role.id,
                    permission_ids=permission_ids,
                )
                role = await self.repo_role.read_role_by_id(role.id)

            await self.log.info(
                tag,
                "Added seeded role",
                {
                    "id": str(role.id),
                    "name": name,
                    "permission_count": len(permission_ids),
                },
            )
            return role
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add seeded role",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e
