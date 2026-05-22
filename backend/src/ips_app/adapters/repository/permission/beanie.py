from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from ips_app.adapters.repository.permission.beanie_model import PermissionDocument
from ips_app.adapters.repository.role.beanie_model import RoleDocument
from ips_app.domain.models.exception import (
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.permission import Permission
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.permission import PermissionRepository


class BeaniePermissionRepository(PermissionRepository):
    def __init__(self, log: LeveledLogging):
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_permission(
        self,
        name: str,
        description: str,
        created_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> Permission:
        tag = f"{self.tag_class}.create_permission"
        session = kwargs.get("session")
        try:
            doc = PermissionDocument(
                name=name,
                description=description,
                created_by=created_by,
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            await self.log.error(
                tag,
                "Duplicate permission name",
                {"error": str(e), "name": name},
            )
            raise DuplicateDomainException("name", "permissions")
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to create permission",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_permission_by_id(
        self,
        id: Any,
        **kwargs: Any,
    ) -> Permission:
        tag = f"{self.tag_class}.read_permission_by_id"
        session = kwargs.get("session")
        try:
            doc = await PermissionDocument.get(
                self._to_obj_id(id),
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(str(id), "permissions")
            return doc.to_domain()
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read permission by id",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_permission_by_name(
        self,
        name: str,
        **kwargs: Any,
    ) -> Permission:
        tag = f"{self.tag_class}.read_permission_by_name"
        session = kwargs.get("session")
        try:
            doc = await PermissionDocument.find_one(
                {"name": name},
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(name, "permissions")
            return doc.to_domain()
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read permission by name",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_permissions_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List[Permission], int]:
        tag = f"{self.tag_class}.read_permissions_by_pagination"
        session = kwargs.get("session")
        try:
            query_filter: Dict[str, Any] = {}
            if cursor_id:
                query_filter["_id"] = {"$gt": self._to_obj_id(cursor_id)}
            if search:
                query_filter["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                ]

            query = PermissionDocument.find(query_filter, session=session)
            total = await query.count()
            query = query.sort("_id")
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read permissions by pagination",
                {"error": str(e), "page": page, "limit": limit},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_permission_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_permission_by_id"
        session = kwargs.get("session")
        try:
            doc = await PermissionDocument.get(
                self._to_obj_id(id),
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(str(id), "permissions")

            update_data: Dict[str, Any] = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
            }
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description

            await doc.set(update_data, session=session)
        except DuplicateKeyError as e:
            await self.log.error(
                tag,
                "Duplicate permission name on update",
                {"error": str(e), "id": str(id), "name": name},
            )
            raise DuplicateDomainException("name", "permissions")
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update permission",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_permission_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_permission_preferences_by_id"
        session = kwargs.get("session")
        try:
            doc = await PermissionDocument.get(
                self._to_obj_id(id),
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(str(id), "permissions")

            now = datetime.now(timezone.utc)
            await doc.set(
                {
                    "preferences": preferences,
                    "updated_at": now,
                    "updated_by": updated_by,
                },
                session=session,
            )
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update permission preferences",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def delete_permission_by_id(self, id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_permission_by_id"
        session = kwargs.get("session")
        try:
            permission_id = self._to_obj_id(id)
            doc = await PermissionDocument.get(
                permission_id,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(str(id), "permissions")

            role = await RoleDocument.find_one(
                {"permissions.$id": permission_id},
                session=session,
            )
            if role:
                raise ForbiddenDomainException("Permission is used by a role.")

            await doc.delete(session=session)
        except (ForbiddenDomainException, NotFoundDomainException):
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to delete permission",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    def _to_obj_id(self, value: Any) -> Any:
        if isinstance(value, str) and PydanticObjectId.is_valid(value):
            return PydanticObjectId(value)
        return value
