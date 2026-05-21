import json
from typing import Any, List, Optional, Tuple

from ips_app_old.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app_old.domain.models.permission import Permission
from ips_app_old.domain.models.role import Role
from ips_app_old.domain.ports.driven.logging.generic import GenericLogging
from ips_app_old.domain.ports.driven.repository.role import RoleRepository
from ips_app_old.domain.ports.driving.http.role import RoleHTTP


class BaseRoleHTTP(RoleHTTP):
    def __init__(self, repo: RoleRepository, log: GenericLogging):
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def add_role(self, name: str, description: str) -> Role:
        tag = f"{self.tag_class}.add_role"
        try:
            role = await self.repo.create_role(name=name, description=description)
            await self.log.info(
                tag,
                "Successfully added role",
                {"id": str(role.id), "name": name},
            )
            return role
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add role",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_role(self, role_id: Any) -> Role:
        tag = f"{self.tag_class}.get_role"
        try:
            return await self.repo.read_role_by_id(role_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get role",
                {"error": str(e), "id": str(role_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_roles(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Role], int]:
        tag = f"{self.tag_class}.get_roles"
        try:
            return await self.repo.read_roles_by_pagination(
                page,
                limit,
                cursor_id,
                search,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get roles",
                {"error": str(e), "page": page, "limit": limit},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_role(
        self,
        role_id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Role:
        tag = f"{self.tag_class}.set_role"
        try:
            await self.repo.update_role_by_id(role_id, name, description)
            role = await self.get_role(role_id)
            await self.log.info(
                tag,
                "Successfully updated role",
                {"id": str(role_id)},
            )
            return role
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set role",
                {"error": str(e), "id": str(role_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_role_preferences(self, role_id: Any, preferences: bytes) -> Role:
        tag = f"{self.tag_class}.set_role_preferences"
        try:
            preferences_dict = json.loads(preferences)
            await self.repo.update_role_preferences_by_id(role_id, preferences_dict)
            role = await self.get_role(role_id)
            await self.log.info(
                tag,
                "Successfully updated role preferences",
                {"id": str(role_id)},
            )
            return role
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set role preferences",
                {"error": str(e), "id": str(role_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_role(self, role_id: Any) -> str:
        tag = f"{self.tag_class}.remove_role"
        try:
            await self.repo.delete_role_by_id(role_id)
            await self.log.info(
                tag,
                "Successfully removed role",
                {"id": str(role_id)},
            )
            return "Role removed successfully"
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove role",
                {"error": str(e), "id": str(role_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def add_permissions_to_role(
        self,
        role_id: Any,
        permission_ids: List[Any],
    ) -> Role:
        tag = f"{self.tag_class}.add_permissions_to_role"
        try:
            await self.repo.add_permissions_to_role(role_id, permission_ids)
            role = await self.get_role(role_id)
            await self.log.info(
                tag,
                "Successfully added permissions to role",
                {
                    "id": str(role_id),
                    "permission_ids": [str(permission_id) for permission_id in permission_ids],
                },
            )
            return role
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add permissions to role",
                {"error": str(e), "id": str(role_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_permissions_from_role(
        self,
        role_id: Any,
        permission_ids: List[Any],
    ) -> Role:
        tag = f"{self.tag_class}.remove_permissions_from_role"
        try:
            await self.repo.remove_permissions_from_role(role_id, permission_ids)
            role = await self.get_role(role_id)
            await self.log.info(
                tag,
                "Successfully removed permissions from role",
                {
                    "id": str(role_id),
                    "permission_ids": [str(permission_id) for permission_id in permission_ids],
                },
            )
            return role
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove permissions from role",
                {"error": str(e), "id": str(role_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_role_permissions(self, role_id: Any) -> List[Permission]:
        tag = f"{self.tag_class}.get_role_permissions"
        try:
            role = await self.get_role(role_id)
            return role.permissions
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get role permissions",
                {"error": str(e), "id": str(role_id)},
            )
            raise UnexpectedDomainException(str(e)) from e
