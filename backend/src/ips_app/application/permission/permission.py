from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.repository.permission import PermissionRepository
from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.permission import Permission
from ips_app.domain.usecases.permission import PermissionUsecase

from ips_app.application._shared.validator import (
    validate_description,
    validate_resource_name,
)


class BasePermissionUsecase(PermissionUsecase):
    def __init__(self, repo: PermissionRepository, log: LeveledLogger) -> None:
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_permission(
        self,
        name: str,
        description: str = "",
        created_by: Optional[Any] = None,
    ) -> Permission:
        tag = f"{self.tag_class}/create_permission"
        try:
            validate_resource_name(name)
            validate_description(description)
            permission = await self.repo.create_permission(
                name=name,
                description=description,
                created_by=created_by,
            )
            await self.log.info(
                tag,
                "Successfully created permission",
                {"id": str(permission.id), "name": name},
            )
            return permission
        except Exception as e:
            await self.log.error(
                tag, "Failed to create permission", {"error": str(e), "name": name}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_permission_by_id(self, id: Any) -> Permission:
        tag = f"{self.tag_class}/get_permission_by_id"
        try:
            permission = await self.repo.read_permission_by_id(id)
            await self.log.info(
                tag, "Successfully retrieved permission", {"id": str(id)}
            )
            return permission
        except Exception as e:
            await self.log.error(
                tag, "Failed to retrieve permission", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_permission_by_name(self, name: str) -> Permission:
        tag = f"{self.tag_class}/get_permission_by_name"
        try:
            permission = await self.repo.read_permission_by_name(name)
            await self.log.info(
                tag, "Successfully retrieved permission", {"name": name}
            )
            return permission
        except Exception as e:
            await self.log.error(
                tag, "Failed to retrieve permission", {"error": str(e), "name": name}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def permission_exists_by_name(self, name: str) -> bool:
        tag = f"{self.tag_class}/permission_exists_by_name"
        try:
            exists = True
            try:
                await self.repo.read_permission_by_name(name)
            except NotFoundDomainException:
                exists = False
            await self.log.info(
                tag,
                "Successfully checked permission existence",
                {"name": name, "exists": exists},
            )
            return exists
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to check permission existence",
                {"error": str(e), "name": name},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_permissions(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
    ) -> Tuple[List[Permission], int]:
        tag = f"{self.tag_class}/get_permissions"
        try:
            permissions, total = await self.repo.read_permissions_by_pagination(
                page=page,
                limit=limit,
                search=search,
            )
            await self.log.info(
                tag,
                "Successfully retrieved permissions",
                {"page": page, "limit": limit, "total": total},
            )
            return permissions, total
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve permissions",
                {"error": str(e), "page": page, "limit": limit},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_permission(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> Permission:
        tag = f"{self.tag_class}/update_permission"
        try:
            if name is not None:
                validate_resource_name(name)
            if description is not None:
                validate_description(description)
            permission = await self.repo.update_permission_by_id(
                id=id,
                name=name,
                description=description,
                updated_by=updated_by,
            )
            await self.log.info(
                tag, "Successfully updated permission", {"id": str(id)}
            )
            return permission
        except Exception as e:
            await self.log.error(
                tag, "Failed to update permission", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_permission_preferences(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> Permission:
        tag = f"{self.tag_class}/update_permission_preferences"
        try:
            permission = await self.repo.update_permission_preferences_by_id(
                id=id,
                preferences=preferences,
                updated_by=updated_by,
            )
            await self.log.info(
                tag, "Successfully updated permission preferences", {"id": str(id)}
            )
            return permission
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update permission preferences",
                {"error": str(e), "id": str(id)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def delete_permission(self, id: Any) -> None:
        tag = f"{self.tag_class}/delete_permission"
        try:
            await self.repo.delete_permission_by_id(id)
            await self.log.info(
                tag, "Successfully deleted permission", {"id": str(id)}
            )
        except Exception as e:
            await self.log.error(
                tag, "Failed to delete permission", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e
