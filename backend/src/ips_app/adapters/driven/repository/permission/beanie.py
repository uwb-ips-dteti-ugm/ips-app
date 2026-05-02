from typing import Optional, List, Tuple, Any, Dict
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from ips_app.domain.models.permission import Permission
from ips_app.ports.driven.repository.permission import PermissionRepositoryPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.domain.models.exception import NotFoundException, DuplicateException
from ips_app.adapters.driven.repository.permission.beanie_model import PermissionDocument


class BeaniePermissionRepository(PermissionRepositoryPort):
    def __init__(self, log: GenericLoggingPort):
        self.log = log
        self.tag_class = "BeaniePermissionRepository"

    async def create_permission(
        self,
        name: str,
        description: str,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> Permission:
        tag = f"{self.tag_class}.create_permission"
        session = kwargs.get("session")
        try:
            doc = PermissionDocument(name=name, description=description, created_by=created_by)
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate permission name", {"error": str(e), "name": name})
            raise DuplicateException("name", "permissions")
        except Exception as e:
            await self.log.error(tag, "Failed to create permission", {"error": str(e)})
            raise e

    async def read_permission_by_id(self, id: Any, **kwargs: Any) -> Optional[Permission]:
        tag = f"{self.tag_class}.read_permission_by_id"
        session = kwargs.get("session")
        try:
            doc = await PermissionDocument.get(id, session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read permission by id", {"error": str(e), "id": str(id)})
            raise e

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
            query = PermissionDocument.find_all(session=session)
            if search:
                query = PermissionDocument.find({"name": {"$regex": search, "$options": "i"}}, session=session)
            if cursor_id:
                query = query.find({"_id": {"$gt": cursor_id}})

            total = await query.count()
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except Exception as e:
            await self.log.error(tag, "Failed to read permissions by pagination", {"error": str(e)})
            raise e

    async def update_permission_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_permission_by_id"
        session = kwargs.get("session")
        try:
            doc = await PermissionDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "permissions")

            update_data: Dict[str, Any] = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description

            await doc.set(update_data, session=session)
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate permission name on update", {"error": str(e), "id": str(id)})
            raise DuplicateException("name", "permissions")
        except NotFoundException:
            raise
        except Exception as e:
            await self.log.error(tag, "Failed to update permission", {"error": str(e), "id": str(id)})
            raise e

    async def update_permission_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_permission_preferences_by_id"
        session = kwargs.get("session")
        try:
            doc = await PermissionDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "permissions")

            await doc.set({
                "preferences": preferences,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update permission preferences", {"error": str(e), "id": str(id)})
            raise e

    async def read_permission_by_name(self, name: str, **kwargs: Any) -> Optional[Permission]:
        tag = f"{self.tag_class}.read_permission_by_name"
        session = kwargs.get("session")
        try:
            doc = await PermissionDocument.find_one({"name": name}, session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read permission by name", {"error": str(e), "name": name})
            raise e

    async def delete_permission_by_id(self, id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_permission_by_id"
        session = kwargs.get("session")
        try:
            doc = await PermissionDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "permissions")
            await doc.delete(session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to delete permission", {"error": str(e), "id": str(id)})
            raise e
