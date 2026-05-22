from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from beanie import PydanticObjectId
from beanie.operators import In
from pymongo.errors import DuplicateKeyError

from ips_app.adapters.repository.permission.beanie_model import PermissionDocument
from ips_app.adapters.repository.role.beanie_model import RoleDocument
from ips_app.adapters.repository.user.beanie_model import UserDocument
from ips_app.domain.models.exception import (
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.permission import Permission
from ips_app.domain.models.role import Role
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.role import RoleRepository


class BeanieRoleRepository(RoleRepository):
    def __init__(self, log: LeveledLogging):
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_role(
        self,
        name: str,
        description: str,
        is_default: bool = False,
        created_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> Role:
        tag = f"{self.tag_class}.create_role"
        session = kwargs.get("session")
        try:
            if is_default:
                existing_default = await RoleDocument.find_one(
                    {"is_default": True},
                    session=session,
                )
                if existing_default:
                    await existing_default.set(
                        {
                            "is_default": False,
                            "updated_at": datetime.now(timezone.utc),
                            "updated_by": created_by,
                        },
                        session=session,
                    )

            doc = RoleDocument(
                name=name,
                description=description,
                is_default=is_default,
                created_by=created_by,
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            await self.log.error(
                tag,
                "Duplicate role name",
                {"error": str(e), "name": name},
            )
            raise DuplicateDomainException("name", "roles")
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to create role",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_role_by_id(self, id: Any, **kwargs: Any) -> Role:
        tag = f"{self.tag_class}.read_role_by_id"
        session = kwargs.get("session")
        try:
            doc = await RoleDocument.get(
                self._to_obj_id(id),
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(str(id), "roles")
            return doc.to_domain()
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read role by id",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_role_by_name(self, name: str, **kwargs: Any) -> Role:
        tag = f"{self.tag_class}.read_role_by_name"
        session = kwargs.get("session")
        try:
            doc = await RoleDocument.find_one(
                {"name": name},
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(name, "roles")
            return doc.to_domain()
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read role by name",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

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
            query_filter: Dict[str, Any] = {}
            if cursor_id:
                query_filter["_id"] = {"$gt": self._to_obj_id(cursor_id)}
            if search:
                query_filter["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                ]

            query = RoleDocument.find(query_filter, fetch_links=True, session=session)
            total = await query.count()
            query = query.sort("_id")
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read roles by pagination",
                {"error": str(e), "page": page, "limit": limit},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_role_default(self, **kwargs: Any) -> Role:
        tag = f"{self.tag_class}.read_role_default"
        session = kwargs.get("session")
        try:
            doc = await RoleDocument.find_one(
                {"is_default": True},
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException("default", "roles")
            return doc.to_domain()
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read default role",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_role_permissions_by_id(
        self,
        id: Any,
        **kwargs: Any,
    ) -> List[Permission]:
        tag = f"{self.tag_class}.read_role_permissions_by_id"
        session = kwargs.get("session")
        try:
            doc = await RoleDocument.get(
                self._to_obj_id(id),
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(str(id), "roles")
            return doc.to_domain().permissions
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read role permissions",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_role_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_role_by_id"
        session = kwargs.get("session")
        try:
            doc = await RoleDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(str(id), "roles")

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
                "Duplicate role name on update",
                {"error": str(e), "id": str(id), "name": name},
            )
            raise DuplicateDomainException("name", "roles")
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update role",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_role_is_default_by_id(
        self,
        id: Any,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_role_is_default_by_id"
        session = kwargs.get("session")
        try:
            role_id = self._to_obj_id(id)
            doc = await RoleDocument.get(role_id, session=session)
            if not doc:
                raise NotFoundDomainException(str(id), "roles")

            now = datetime.now(timezone.utc)
            existing_default = await RoleDocument.find_one(
                {"is_default": True},
                session=session,
            )
            if existing_default and str(existing_default.id) != str(doc.id):
                await existing_default.set(
                    {
                        "is_default": False,
                        "updated_at": now,
                        "updated_by": updated_by,
                    },
                    session=session,
                )

            await doc.set(
                {
                    "is_default": True,
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
                "Failed to set default role",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_role_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_role_preferences_by_id"
        session = kwargs.get("session")
        try:
            doc = await RoleDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(str(id), "roles")

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
                "Failed to update role preferences",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def delete_role_by_id(self, id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_role_by_id"
        session = kwargs.get("session")
        try:
            role_id = self._to_obj_id(id)
            doc = await RoleDocument.get(role_id, session=session)
            if not doc:
                raise NotFoundDomainException(str(id), "roles")

            user = await UserDocument.find_one(
                {"role.$id": role_id},
                session=session,
            )
            if user:
                raise ForbiddenDomainException("Role is used by a user.")

            await doc.delete(session=session)
        except (ForbiddenDomainException, NotFoundDomainException):
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to delete role",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def add_permissions_to_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.add_permissions_to_role"
        session = kwargs.get("session")
        try:
            doc = await RoleDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(str(id), "roles")

            permissions = await self._read_permission_documents(permission_ids, session)
            existing_ids = {
                str(permission_id)
                for permission_id in (self._permission_link_id(permission) for permission in doc.permissions)
                if permission_id is not None
            }

            added_count = 0
            for permission in permissions:
                if str(permission.id) not in existing_ids:
                    doc.permissions.append(permission)  # type: ignore[arg-type]
                    added_count += 1

            if added_count:
                doc.updated_at = datetime.now(timezone.utc)
                doc.updated_by = updated_by
                await doc.save(session=session)
                await self.log.info(
                    tag,
                    "Added permissions to role",
                    {"id": str(id), "count": added_count},
                )
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add permissions to role",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_permissions_from_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.remove_permissions_from_role"
        session = kwargs.get("session")
        try:
            doc = await RoleDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(str(id), "roles")

            ids_to_remove = {str(self._to_obj_id(permission_id)) for permission_id in permission_ids}
            permissions = [
                permission
                for permission in doc.permissions
                if str(self._permission_link_id(permission)) not in ids_to_remove
            ]

            if len(permissions) != len(doc.permissions):
                doc.permissions = permissions
                doc.updated_at = datetime.now(timezone.utc)
                doc.updated_by = updated_by
                await doc.save(session=session)
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove permissions from role",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    def _to_obj_id(self, value: Any) -> Any:
        if isinstance(value, str) and PydanticObjectId.is_valid(value):
            return PydanticObjectId(value)
        return value

    def _permission_link_id(self, permission: Any) -> Any:
        if isinstance(permission, PermissionDocument):
            return permission.id
        if permission_ref := getattr(permission, "ref", None):
            return permission_ref.id
        if permission_value := getattr(permission, "value", None):
            return permission_value.id
        return None

    async def _read_permission_documents(
        self,
        permission_ids: List[Any],
        session: Any,
    ) -> List[PermissionDocument]:
        ids = [self._to_obj_id(permission_id) for permission_id in permission_ids]
        if not ids:
            return []

        docs = await PermissionDocument.find(
            In(PermissionDocument.id, ids),
            session=session,
        ).to_list()
        found_ids = {str(doc.id) for doc in docs}
        missing_ids = [str(permission_id) for permission_id in ids if str(permission_id) not in found_ids]
        if missing_ids:
            raise NotFoundDomainException(", ".join(missing_ids), "permissions")

        return docs
