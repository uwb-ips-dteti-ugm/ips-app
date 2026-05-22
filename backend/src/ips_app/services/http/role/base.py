from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.permission import Permission
from ips_app.domain.models.role import Role
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.role import RoleRepository
from ips_app.domain.ports.driving.http.role import RoleHTTP


class BaseRoleHTTP(RoleHTTP):
    def __init__(self, repo: RoleRepository, log: LeveledLogging):
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def add_role(
        self,
        name: str,
        description: str = "",
        is_default: bool = False,
        created_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}.add_role"
        try:
            role = await self.repo.create_role(
                name=name,
                description=description,
                is_default=is_default,
                created_by=created_by,
            )
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

    async def get_default_role(self) -> Role:
        tag = f"{self.tag_class}.get_default_role"
        try:
            return await self.repo.read_role_default()
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get default role",
                {"error": str(e)},
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
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
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
        updated_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}.set_role"
        try:
            await self.repo.update_role_by_id(
                id=role_id,
                name=name,
                description=description,
                updated_by=updated_by,
            )
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

    async def set_default_role(
        self,
        role_id: Any,
        updated_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}.set_default_role"
        try:
            await self.repo.update_role_is_default_by_id(
                id=role_id,
                updated_by=updated_by,
            )
            role = await self.get_role(role_id)
            await self.log.info(
                tag,
                "Successfully set default role",
                {"id": str(role_id)},
            )
            return role
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set default role",
                {"error": str(e), "id": str(role_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_role_preferences(
        self,
        role_id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}.set_role_preferences"
        try:
            await self.repo.update_role_preferences_by_id(
                id=role_id,
                preferences=preferences,
                updated_by=updated_by,
            )
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
        updated_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}.add_permissions_to_role"
        try:
            await self.repo.add_permissions_to_role(
                id=role_id,
                permission_ids=permission_ids,
                updated_by=updated_by,
            )
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
        updated_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}.remove_permissions_from_role"
        try:
            await self.repo.remove_permissions_from_role(
                id=role_id,
                permission_ids=permission_ids,
                updated_by=updated_by,
            )
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
            return await self.repo.read_role_permissions_by_id(role_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get role permissions",
                {"error": str(e), "id": str(role_id)},
            )
            raise UnexpectedDomainException(str(e)) from e
