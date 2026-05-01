from typing import Optional, List, Tuple, Any, Dict
from ips_app.domain.models.role import Role
from ips_app.domain.models.permission import Permission
from ips_app.ports.driven.repository.role import RoleRepositoryPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.domain.models.exception import NotFoundException, DuplicateException
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from beanie.operators import In

class BeanieRoleRepository(RoleRepositoryPort):
    def __init__(self, log: GenericLoggingPort):
        self.log = log
        self.tag_class = "BeanieRoleRepository"

    async def create_role(
        self, 
        name: str, 
        description: str, 
        is_default: bool = False, 
        created_by: Optional[int] = None
    ) -> Role:
        tag = f"{self.tag_class}.create_role"
        try:
            if is_default:
                existing_default = await Role.find_one({"is_default": True})
                if existing_default:
                    existing_default.is_default = False
                    await existing_default.save()
            
            role = Role(name=name, description=description, is_default=is_default, created_by=created_by)
            await role.insert()
            return role
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate role name", {"error": str(e), "name": name})
            raise DuplicateException("name", "roles")
        except Exception as e:
            await self.log.error(tag, "Failed to create role", {"error": str(e)})
            raise e

    async def read_role_by_id(self, id: Any) -> Optional[Role]:
        tag = f"{self.tag_class}.read_role_by_id"
        try:
            return await Role.get(id, fetch_links=True)
        except Exception as e:
            await self.log.error(tag, "Failed to read role by id", {"error": str(e), "id": str(id)})
            raise e

    async def read_roles_by_pagination(
        self, 
        page: int, 
        limit: int, 
        cursor_id: Optional[Any] = None, 
        search: Optional[str] = None
    ) -> Tuple[List[Role], int]:
        tag = f"{self.tag_class}.read_roles_by_pagination"
        try:
            query = Role.find_all()
            if search:
                query = Role.find({"name": {"$regex": search, "$options": "i"}})
            
            if cursor_id:
                query = query.find({"_id": {"$gt": cursor_id}})
            
            total = await query.count()
            items = await query.skip(page * limit).limit(limit).to_list()
            return items, total
        except Exception as e:
            await self.log.error(tag, "Failed to read roles by pagination", {"error": str(e)})
            raise e

    async def read_role_default(self) -> Optional[Role]:
        tag = f"{self.tag_class}.read_role_default"
        try:
            return await Role.find_one({"is_default": True}, fetch_links=True)
        except Exception as e:
            await self.log.error(tag, "Failed to read default role", {"error": str(e)})
            raise e

    async def update_role_by_id(
        self, 
        id: Any, 
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        updated_by: Optional[int] = None
    ) -> None:
        tag = f"{self.tag_class}.update_role_by_id"
        try:
            role = await Role.get(id)
            if not role:
                raise NotFoundException(str(id), "roles")
            
            update_data = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": role.version + 1
            }
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            
            await role.set(update_data)
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate role name on update", {"error": str(e), "id": str(id)})
            raise DuplicateException("name", "roles")
        except NotFoundException:
            raise
        except Exception as e:
            await self.log.error(tag, "Failed to update role", {"error": str(e), "id": str(id)})
            raise e

    async def update_role_is_default_by_id(self, id: Any, updated_by: Optional[int] = None) -> None:
        tag = f"{self.tag_class}.update_role_is_default_by_id"
        try:
            # Unset all default roles
            existing_default = await Role.find_one({"is_default": True})
            if existing_default:
                existing_default.is_default = False
                await existing_default.save()
            
            role = await Role.get(id)
            if not role:
                raise NotFoundException(str(id), "roles")
            
            await role.set({
                "is_default": True,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": role.version + 1
            })
        except NotFoundException:
            raise
        except Exception as e:
            await self.log.error(tag, "Failed to set default role", {"error": str(e), "id": str(id)})
            raise e

    async def update_role_preferences_by_id(
        self, 
        id: Any, 
        preferences: Dict[str, Any], 
        updated_by: Optional[int] = None
    ) -> None:
        tag = f"{self.tag_class}.update_role_preferences_by_id"
        try:
            role = await Role.get(id)
            if not role:
                raise NotFoundException(str(id), "roles")
            
            await role.set({
                "preferences": preferences,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": role.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to update role preferences", {"error": str(e), "id": str(id)})
            raise e

    async def delete_role_by_id(self, id: Any) -> None:
        tag = f"{self.tag_class}.delete_role_by_id"
        try:
            role = await Role.get(id)
            if not role:
                raise NotFoundException(str(id), "roles")
            await role.delete()
        except Exception as e:
            await self.log.error(tag, "Failed to delete role", {"error": str(e), "id": str(id)})
            raise e

    async def add_permissions_to_role(self, id: Any, permission_ids: List[Any], updated_by: Optional[int] = None) -> None:
        tag = f"{self.tag_class}.add_permissions_to_role"
        try:
            role = await Role.get(id)
            if not role:
                raise NotFoundException(str(id), "roles")
            
            permissions = await Permission.find(In(Permission.id, permission_ids)).to_list()
            
            # Using a set of ID strings to avoid duplicates
            existing_ids = {str(link.ref.id) for link in role.permissions}
            
            for perm in permissions:
                if str(perm.id) not in existing_ids:
                    role.permissions.append(perm) # type: ignore
                
            await role.set({
                "permissions": role.permissions,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": role.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to add permissions to role", {"error": str(e), "id": str(id)})
            raise e

    async def remove_permissions_from_role(self, id: Any, permission_ids: List[Any], updated_by: Optional[int] = None) -> None:
        tag = f"{self.tag_class}.remove_permissions_from_role"
        try:
            role = await Role.get(id)
            if not role:
                raise NotFoundException(str(id), "roles")
            
            str_ids = {str(pid) for pid in permission_ids}
            role.permissions = [p for p in role.permissions if str(p.ref.id) not in str_ids]
            
            await role.set({
                "permissions": role.permissions,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": role.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to remove permissions from role", {"error": str(e), "id": str(id)})
            raise e
