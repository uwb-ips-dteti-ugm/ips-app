import json
from typing import Any, List, Optional, Tuple

from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.permission import Permission
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.repository.permission import PermissionRepository
from ips_app.domain.ports.driving.http.permission import PermissionHTTP


class BasePermissionHTTP(PermissionHTTP):
    def __init__(self, repo: PermissionRepository, log: GenericLogging):
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def add_permission(self, name: str, description: str) -> Permission:
        tag = f"{self.tag_class}.add_permission"
        try:
            permission = await self.repo.create_permission(
                name=name,
                description=description,
            )
            await self.log.info(
                tag,
                "Successfully added permission",
                {"id": str(permission.id), "name": name},
            )
            return permission
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add permission",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_permission(self, permission_id: Any) -> Permission:
        tag = f"{self.tag_class}.get_permission"
        try:
            return await self.repo.read_permission_by_id(permission_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get permission",
                {"error": str(e), "id": str(permission_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_permissions(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Permission], int]:
        tag = f"{self.tag_class}.get_permissions"
        try:
            return await self.repo.read_permissions_by_pagination(
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
                "Failed to get permissions",
                {"error": str(e), "page": page, "limit": limit},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_permission(
        self,
        permission_id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Permission:
        tag = f"{self.tag_class}.set_permission"
        try:
            await self.repo.update_permission_by_id(
                permission_id,
                name,
                description,
            )
            permission = await self.get_permission(permission_id)
            await self.log.info(
                tag,
                "Successfully updated permission",
                {"id": str(permission_id)},
            )
            return permission
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set permission",
                {"error": str(e), "id": str(permission_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_permission_preferences(
        self,
        permission_id: Any,
        preferences: bytes,
    ) -> Permission:
        tag = f"{self.tag_class}.set_permission_preferences"
        try:
            preferences_dict = json.loads(preferences)
            await self.repo.update_permission_preferences_by_id(
                permission_id,
                preferences_dict,
            )
            permission = await self.get_permission(permission_id)
            await self.log.info(
                tag,
                "Successfully updated permission preferences",
                {"id": str(permission_id)},
            )
            return permission
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set permission preferences",
                {"error": str(e), "id": str(permission_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_permission(self, permission_id: Any) -> str:
        tag = f"{self.tag_class}.remove_permission"
        try:
            await self.repo.delete_permission_by_id(permission_id)
            await self.log.info(
                tag,
                "Successfully removed permission",
                {"id": str(permission_id)},
            )
            return "Permission removed successfully"
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove permission",
                {"error": str(e), "id": str(permission_id)},
            )
            raise UnexpectedDomainException(str(e)) from e
