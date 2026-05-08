from typing import Optional, List, Tuple, Any, Dict
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from beanie.operators import In
from beanie import PydanticObjectId
from ips_app_old.domain.models.role import Role
from ips_app_old.ports.driven.repository.role import RoleRepository
from ips_app_old.ports.driven.logging.generic import GenericLoggingPort
from ips_app_old.domain.models.exception import NotFoundException, DuplicateException
from ips_app_old.adapters.driven.repository.role.beanie_model import RoleDocument
from ips_app_old.adapters.driven.repository.permission.beanie_model import PermissionDocument


class BeanieRoleRepository(RoleRepository):
    def __init__(self, log: GenericLoggingPort):
        self.log = log
        self.tag_class = "BeanieRoleRepository"

    async def create_role(
        self,
        name: str,
        description: str,
        is_default: bool = False,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> Role:
        tag = f"{self.tag_class}.create_role"
        session = kwargs.get("session")
        try:
            if is_default:
                existing_default = await RoleDocument.find_one({"is_default": True}, session=session)
                if existing_default:
                    existing_default.is_default = False
                    await existing_default.save(session=session)

            doc = RoleDocument(name=name, description=description, is_default=is_default, created_by=created_by)
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate role name", {"error": str(e), "name": name})
            raise DuplicateException("name", "roles")
        except Exception as e:
            await self.log.error(tag, "Failed to create role", {"error": str(e)})
            raise e

    async def read_role_by_id(self, id: Any, **kwargs: Any) -> Optional[Role]:
        tag = f"{self.tag_class}.read_role_by_id"
        session = kwargs.get("session")
        try:
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await RoleDocument.get(id, fetch_links=True, session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read role by id", {"error": str(e), "id": str(id)})
            raise e

    async def read_roles_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List[Role], int]:
        tag = f"{self.tag_class}.read_roles_by_pagination"
        session = kwargs.get("session")
        try:
            query = RoleDocument.find_all(session=session)
            if search:
                query = RoleDocument.find({"name": {"$regex": search, "$options": "i"}}, session=session)
            if cursor_id:
                if isinstance(cursor_id, str) and PydanticObjectId.is_valid(cursor_id):
                    cursor_id = PydanticObjectId(cursor_id)
                query = query.find({"_id": {"$gt": cursor_id}})

            total = await query.count()
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except Exception as e:
            await self.log.error(tag, "Failed to read roles by pagination", {"error": str(e)})
            raise e

    async def read_role_by_name(self, name: str, **kwargs: Any) -> Optional[Role]:
        tag = f"{self.tag_class}.read_role_by_name"
        session = kwargs.get("session")
        try:
            doc = await RoleDocument.find_one({"name": name}, fetch_links=True, session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read role by name", {"error": str(e), "name": name})
            raise e

    async def read_role_default(self, **kwargs: Any) -> Optional[Role]:
        tag = f"{self.tag_class}.read_role_default"
        session = kwargs.get("session")
        try:
            doc = await RoleDocument.find_one({"is_default": True}, fetch_links=True, session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read default role", {"error": str(e)})
            raise e

    async def update_role_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_role_by_id"
        session = kwargs.get("session")
        try:
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await RoleDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "roles")

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
            await self.log.error(tag, "Duplicate role name on update", {"error": str(e), "id": str(id)})
            raise DuplicateException("name", "roles")
        except NotFoundException:
            raise
        except Exception as e:
            await self.log.error(tag, "Failed to update role", {"error": str(e), "id": str(id)})
            raise e

    async def update_role_is_default_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_role_is_default_by_id"
        session = kwargs.get("session")
        try:
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            existing_default = await RoleDocument.find_one({"is_default": True}, session=session)
            if existing_default:
                existing_default.is_default = False
                await existing_default.save(session=session)

            doc = await RoleDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "roles")

            await doc.set({
                "is_default": True,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except NotFoundException:
            raise
        except Exception as e:
            await self.log.error(tag, "Failed to set default role", {"error": str(e), "id": str(id)})
            raise e

    async def update_role_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_role_preferences_by_id"
        session = kwargs.get("session")
        try:
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await RoleDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "roles")

            await doc.set({
                "preferences": preferences,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update role preferences", {"error": str(e), "id": str(id)})
            raise e

    async def delete_role_by_id(self, id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_role_by_id"
        session = kwargs.get("session")
        try:
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await RoleDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "roles")
            await doc.delete(session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to delete role", {"error": str(e), "id": str(id)})
            raise e

    async def add_permissions_to_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.add_permissions_to_role"
        session = kwargs.get("session")
        try:
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await RoleDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "roles")

            # Convert permission_ids to ObjectIds for the query
            valid_ids = [PydanticObjectId(pid) if isinstance(pid, str) and PydanticObjectId.is_valid(pid) else pid for pid in permission_ids]
            
            permissions = await PermissionDocument.find(
                In(PermissionDocument.id, valid_ids), session=session
            ).to_list()

            existing_ids = {
                str(link.id if isinstance(link, PermissionDocument) else link.ref.id)
                for link in doc.permissions
            }
            
            added_count = 0
            for perm in permissions:
                if str(perm.id) not in existing_ids:
                    doc.permissions.append(perm)  # type: ignore
                    added_count += 1

            if added_count > 0:
                doc.updated_at = datetime.now(timezone.utc)
                doc.updated_by = updated_by
                doc.version += 1
                await doc.save(session=session)
                await self.log.info(tag, f"Added {added_count} permissions to role", {"id": str(id), "count": added_count})
            
        except Exception as e:
            await self.log.error(tag, "Failed to add permissions to role", {"error": str(e), "id": str(id)})
            raise e

    async def remove_permissions_from_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.remove_permissions_from_role"
        session = kwargs.get("session")
        try:
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await RoleDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "roles")

            str_ids = {str(pid) for pid in permission_ids}
            new_permissions = [
                p for p in doc.permissions 
                if str(p.id if isinstance(p, PermissionDocument) else p.ref.id) not in str_ids
            ]

            if len(new_permissions) != len(doc.permissions):
                doc.permissions = new_permissions
                doc.updated_at = datetime.now(timezone.utc)
                doc.updated_by = updated_by
                doc.version += 1
                await doc.save(session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to remove permissions from role", {"error": str(e), "id": str(id)})
            raise e
