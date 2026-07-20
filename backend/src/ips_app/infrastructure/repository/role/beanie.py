from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from beanie.exceptions import RevisionIdWasChanged
from beanie.operators import In
from pymongo.errors import DuplicateKeyError

from ips_app.domain.contracts.repository.role import RoleRepository
from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.permission import Permission
from ips_app.domain.models.role import Role
from ips_app.infrastructure.repository._shared.link import link_id
from ips_app.infrastructure.repository._shared.object_id import get_by_id, to_object_id
from ips_app.infrastructure.repository._shared.pagination import paginate
from ips_app.infrastructure.repository.permission.beanie_model import (
    PermissionDocument,
)
from ips_app.infrastructure.repository.role.beanie_model import RoleDocument
from ips_app.infrastructure.repository.user.beanie_model import UserDocument


class BeanieRoleRepository(RoleRepository):
    async def create_role(
        self,
        name: str,
        description: str = "",
        is_default: bool = False,
        created_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role:
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
            raise DuplicateDomainException(f"Role name '{name}' already exists") from e
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_role_by_id(self, id: Any, session: Optional[Any] = None) -> Role:
        try:
            doc = await get_by_id(RoleDocument, id, fetch_links=True, session=session)
            if not doc:
                raise NotFoundDomainException(f"Role '{id}' not found")
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_role_by_name(self, name: str, session: Optional[Any] = None) -> Role:
        try:
            doc = await RoleDocument.find_one(
                {"name": name},
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(f"Role '{name}' not found")
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_roles_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[Role], int]:
        try:
            query_filter: Dict[str, Any] = {}
            if search:
                query_filter["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                ]

            query = RoleDocument.find(query_filter, fetch_links=True, session=session)
            return await paginate(query, page, limit, RoleDocument.to_domain)
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_role_default(self, session: Optional[Any] = None) -> Role:
        try:
            doc = await RoleDocument.find_one(
                {"is_default": True},
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException("Default role not found")
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_role_permissions_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> List[Permission]:
        try:
            doc = await get_by_id(RoleDocument, id, fetch_links=True, session=session)
            if not doc:
                raise NotFoundDomainException(f"Role '{id}' not found")
            return doc.to_domain().permissions
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_role_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role:
        try:
            doc = await get_by_id(RoleDocument, id, fetch_links=True, session=session)
            if not doc:
                raise NotFoundDomainException(f"Role '{id}' not found")

            update_data: Dict[str, Any] = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
            }
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description

            await doc.set(update_data, session=session)
            return doc.to_domain()
        except (DuplicateKeyError, RevisionIdWasChanged) as e:
            # Beanie's Document.update() internally catches DuplicateKeyError from the
            # underlying write and always re-raises it as RevisionIdWasChanged (empty
            # message), so a unique-index violation via `.set()` never actually
            # surfaces as DuplicateKeyError here, only as RevisionIdWasChanged.
            raise DuplicateDomainException(f"Role name '{name}' already exists") from e
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_role_is_default_by_id(
        self,
        id: Any,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role:
        try:
            role_id = to_object_id(id)
            doc = await get_by_id(RoleDocument, role_id, fetch_links=True, session=session)
            if not doc:
                raise NotFoundDomainException(f"Role '{id}' not found")

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
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_role_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role:
        try:
            doc = await get_by_id(RoleDocument, id, fetch_links=True, session=session)
            if not doc:
                raise NotFoundDomainException(f"Role '{id}' not found")

            await doc.set(
                {
                    "preferences": preferences,
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": updated_by,
                },
                session=session,
            )
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def delete_role_by_id(self, id: Any, session: Optional[Any] = None) -> None:
        try:
            role_id = to_object_id(id)
            doc = await get_by_id(RoleDocument, role_id, session=session)
            if not doc:
                raise NotFoundDomainException(f"Role '{id}' not found")

            user = await UserDocument.find_one(
                {"role.$id": role_id},
                session=session,
            )
            if user:
                raise ForbiddenDomainException("Role is used by a user.")

            await doc.delete(session=session)
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def add_permissions_to_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role:
        try:
            doc = await get_by_id(RoleDocument, id, fetch_links=True, session=session)
            if not doc:
                raise NotFoundDomainException(f"Role '{id}' not found")

            permissions = await self._read_permission_documents(permission_ids, session)
            existing_ids = {
                str(existing_id)
                for existing_id in (link_id(permission) for permission in doc.permissions)
                if existing_id is not None
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

            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def remove_permissions_from_role(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Role:
        try:
            doc = await get_by_id(RoleDocument, id, fetch_links=True, session=session)
            if not doc:
                raise NotFoundDomainException(f"Role '{id}' not found")

            ids_to_remove = {str(to_object_id(permission_id)) for permission_id in permission_ids}
            permissions = [
                permission
                for permission in doc.permissions
                if str(link_id(permission)) not in ids_to_remove
            ]

            if len(permissions) != len(doc.permissions):
                doc.permissions = permissions
                doc.updated_at = datetime.now(timezone.utc)
                doc.updated_by = updated_by
                await doc.save(session=session)

            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def _read_permission_documents(
        self,
        permission_ids: List[Any],
        session: Optional[Any],
    ) -> List[PermissionDocument]:
        ids = [to_object_id(permission_id) for permission_id in permission_ids]
        if not ids:
            return []

        docs = await PermissionDocument.find(
            In(PermissionDocument.id, ids),
            session=session,
        ).to_list()
        found_ids = {str(doc.id) for doc in docs}
        missing_ids = [str(permission_id) for permission_id in ids if str(permission_id) not in found_ids]
        if missing_ids:
            raise NotFoundDomainException(f"Permissions not found: {', '.join(missing_ids)}")

        return docs
