from typing import Optional, List, Tuple, Any, Dict
from ips_app.domain.models.permission import Permission
from ips_app.ports.driven.repository.permission import PermissionRepositoryPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.domain.models.exception import NotFoundException, DuplicateException
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone

class BeaniePermissionRepository(PermissionRepositoryPort):
    def __init__(self, log: GenericLoggingPort):
        self.log = log
        self.tag_class = "BeaniePermissionRepository"

    async def create_permission(
        self, 
        name: str, 
        description: str, 
        created_by: Optional[int] = None
    ) -> Permission:
        tag = f"{self.tag_class}.create_permission"
        try:
            permission = Permission(name=name, description=description, created_by=created_by)
            await permission.insert()
            return permission
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate permission name", {"error": str(e), "name": name})
            raise DuplicateException("name", "permissions")
        except Exception as e:
            await self.log.error(tag, "Failed to create permission", {"error": str(e)})
            raise e

    async def read_permission_by_id(self, id: Any) -> Optional[Permission]:
        tag = f"{self.tag_class}.read_permission_by_id"
        try:
            return await Permission.get(id)
        except Exception as e:
            await self.log.error(tag, "Failed to read permission by id", {"error": str(e), "id": str(id)})
            raise e

    async def read_permissions_by_pagination(
        self, 
        page: int, 
        limit: int, 
        cursor_id: Optional[Any] = None, 
        search: Optional[str] = None
    ) -> Tuple[List[Permission], int]:
        tag = f"{self.tag_class}.read_permissions_by_pagination"
        try:
            query = Permission.find_all()
            if search:
                query = Permission.find({"name": {"$regex": search, "$options": "i"}})
            
            if cursor_id:
                query = query.find({"_id": {"$gt": cursor_id}})
            
            total = await query.count()
            items = await query.skip(page * limit).limit(limit).to_list()
            return items, total
        except Exception as e:
            await self.log.error(tag, "Failed to read permissions by pagination", {"error": str(e)})
            raise e

    async def update_permission_by_id(
        self, 
        id: Any, 
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        updated_by: Optional[int] = None
    ) -> None:
        tag = f"{self.tag_class}.update_permission_by_id"
        try:
            permission = await Permission.get(id)
            if not permission:
                raise NotFoundException(str(id), "permissions")
            
            update_data = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": permission.version + 1
            }
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            
            await permission.set(update_data)
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
        updated_by: Optional[int] = None
    ) -> None:
        tag = f"{self.tag_class}.update_permission_preferences_by_id"
        try:
            permission = await Permission.get(id)
            if not permission:
                raise NotFoundException(str(id), "permissions")
            
            await permission.set({
                "preferences": preferences,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": permission.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to update permission preferences", {"error": str(e), "id": str(id)})
            raise e

    async def delete_permission_by_id(self, id: Any) -> None:
        tag = f"{self.tag_class}.delete_permission_by_id"
        try:
            permission = await Permission.get(id)
            if not permission:
                raise NotFoundException(str(id), "permissions")
            await permission.delete()
        except Exception as e:
            await self.log.error(tag, "Failed to delete permission", {"error": str(e), "id": str(id)})
            raise e
