from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.repository.role import RoleRepository
from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.permission import Permission
from ips_app.domain.models.role import Role
from ips_app.domain.usecases.role import RoleUsecase

from ips_app.application._shared.validator import (
    validate_description,
    validate_ids_list,
    validate_resource_name,
)


class BaseRoleUsecase(RoleUsecase):
    def __init__(self, repo: RoleRepository, log: LeveledLogger) -> None:
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_role(
        self,
        name: str,
        description: str = "",
        is_default: bool = False,
        created_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}/create_role"
        try:
            validate_resource_name(name)
            validate_description(description)
            role = await self.repo.create_role(
                name=name,
                description=description,
                is_default=is_default,
                created_by=created_by,
            )
            await self.log.info(
                tag, "Successfully created role", {"id": str(role.id), "name": name}
            )
            return role
        except Exception as e:
            await self.log.error(
                tag, "Failed to create role", {"error": str(e), "name": name}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_role_by_id(self, id: Any) -> Role:
        tag = f"{self.tag_class}/get_role_by_id"
        try:
            role = await self.repo.read_role_by_id(id)
            await self.log.info(tag, "Successfully retrieved role", {"id": str(id)})
            return role
        except Exception as e:
            await self.log.error(
                tag, "Failed to retrieve role", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_role_by_name(self, name: str) -> Role:
        tag = f"{self.tag_class}/get_role_by_name"
        try:
            role = await self.repo.read_role_by_name(name)
            await self.log.info(tag, "Successfully retrieved role", {"name": name})
            return role
        except Exception as e:
            await self.log.error(
                tag, "Failed to retrieve role", {"error": str(e), "name": name}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def role_exists_by_name(self, name: str) -> bool:
        tag = f"{self.tag_class}/role_exists_by_name"
        try:
            exists = True
            try:
                await self.repo.read_role_by_name(name)
            except NotFoundDomainException:
                exists = False
            await self.log.info(
                tag,
                "Successfully checked role existence",
                {"name": name, "exists": exists},
            )
            return exists
        except Exception as e:
            await self.log.error(
                tag, "Failed to check role existence", {"error": str(e), "name": name}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_default_role(self) -> Role:
        tag = f"{self.tag_class}/get_default_role"
        try:
            role = await self.repo.read_role_default()
            await self.log.info(tag, "Successfully retrieved default role", {})
            return role
        except Exception as e:
            await self.log.error(
                tag, "Failed to retrieve default role", {"error": str(e)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_roles(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
    ) -> Tuple[List[Role], int]:
        tag = f"{self.tag_class}/get_roles"
        try:
            roles, total = await self.repo.read_roles_by_pagination(
                page=page,
                limit=limit,
                search=search,
            )
            await self.log.info(
                tag,
                "Successfully retrieved roles",
                {"page": page, "limit": limit, "total": total},
            )
            return roles, total
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve roles",
                {"error": str(e), "page": page, "limit": limit},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_role_permissions(self, id: Any) -> List[Permission]:
        tag = f"{self.tag_class}/get_role_permissions"
        try:
            permissions = await self.repo.read_role_permissions_by_id(id)
            await self.log.info(
                tag, "Successfully retrieved role permissions", {"id": str(id)}
            )
            return permissions
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve role permissions",
                {"error": str(e), "id": str(id)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_role(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}/update_role"
        try:
            if name is not None:
                validate_resource_name(name)
            if description is not None:
                validate_description(description)
            role = await self.repo.update_role_by_id(
                id=id,
                name=name,
                description=description,
                updated_by=updated_by,
            )
            await self.log.info(tag, "Successfully updated role", {"id": str(id)})
            return role
        except Exception as e:
            await self.log.error(
                tag, "Failed to update role", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def set_default_role(
        self,
        id: Any,
        updated_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}/set_default_role"
        try:
            role = await self.repo.update_role_is_default_by_id(
                id=id,
                updated_by=updated_by,
            )
            await self.log.info(
                tag, "Successfully set default role", {"id": str(id)}
            )
            return role
        except Exception as e:
            await self.log.error(
                tag, "Failed to set default role", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_role_preferences(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}/update_role_preferences"
        try:
            role = await self.repo.update_role_preferences_by_id(
                id=id,
                preferences=preferences,
                updated_by=updated_by,
            )
            await self.log.info(
                tag, "Successfully updated role preferences", {"id": str(id)}
            )
            return role
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update role preferences",
                {"error": str(e), "id": str(id)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def delete_role(self, id: Any) -> None:
        tag = f"{self.tag_class}/delete_role"
        try:
            await self.repo.delete_role_by_id(id)
            await self.log.info(tag, "Successfully deleted role", {"id": str(id)})
        except Exception as e:
            await self.log.error(
                tag, "Failed to delete role", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def add_permissions_to_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}/add_permissions_to_role"
        try:
            validate_ids_list(permission_ids, "permission_ids")
            role = await self.repo.add_permissions_to_role(
                id=id,
                permission_ids=permission_ids,
                updated_by=updated_by,
            )
            await self.log.info(
                tag,
                "Successfully added permissions to role",
                {"id": str(id), "permission_ids": [str(pid) for pid in permission_ids]},
            )
            return role
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add permissions to role",
                {"error": str(e), "id": str(id)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def remove_permissions_from_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
    ) -> Role:
        tag = f"{self.tag_class}/remove_permissions_from_role"
        try:
            validate_ids_list(permission_ids, "permission_ids")
            role = await self.repo.remove_permissions_from_role(
                id=id,
                permission_ids=permission_ids,
                updated_by=updated_by,
            )
            await self.log.info(
                tag,
                "Successfully removed permissions from role",
                {"id": str(id), "permission_ids": [str(pid) for pid in permission_ids]},
            )
            return role
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove permissions from role",
                {"error": str(e), "id": str(id)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e
