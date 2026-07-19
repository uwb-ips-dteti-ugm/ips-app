from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.permission import Permission
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.permission import PermissionRepository
from ips_app.domain.ports.driving.seeder.permission import PermissionSeeder


class BasePermissionSeeder(PermissionSeeder):
    def __init__(self, repo: PermissionRepository, log: LeveledLogging):
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def permission_exists(self, name: str) -> bool:
        tag = f"{self.tag_class}.permission_exists"
        try:
            await self.repo.read_permission_by_name(name)
            return True
        except NotFoundDomainException:
            return False
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to check permission existence",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def add_permission(
        self,
        name: str,
        description: str = "",
    ) -> Permission:
        tag = f"{self.tag_class}.add_permission"
        try:
            permission = await self.repo.create_permission(
                name=name,
                description=description,
            )
            await self.log.info(
                tag,
                "Added seeded permission",
                {"id": str(permission.id), "name": name},
            )
            return permission
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add seeded permission",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e
