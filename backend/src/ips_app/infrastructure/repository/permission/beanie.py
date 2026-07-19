from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pymongo.errors import DuplicateKeyError

from ips_app.domain.contracts.repository.permission import PermissionRepository
from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.permission import Permission
from ips_app.infrastructure.repository._shared.object_id import to_object_id
from ips_app.infrastructure.repository._shared.pagination import paginate
from ips_app.infrastructure.repository.permission.beanie_model import (
    PermissionDocument,
)
from ips_app.infrastructure.repository.role.beanie_model import RoleDocument


class BeaniePermissionRepository(PermissionRepository):
    async def create_permission(
        self,
        name: str,
        description: str = "",
        created_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Permission:
        try:
            doc = PermissionDocument(
                name=name,
                description=description,
                created_by=created_by,
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            raise DuplicateDomainException(
                f"Permission name '{name}' already exists"
            ) from e
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_permission_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> Permission:
        try:
            doc = await PermissionDocument.get(to_object_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(f"Permission '{id}' not found")
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_permission_by_name(
        self,
        name: str,
        session: Optional[Any] = None,
    ) -> Permission:
        try:
            doc = await PermissionDocument.find_one({"name": name}, session=session)
            if not doc:
                raise NotFoundDomainException(f"Permission '{name}' not found")
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_permissions_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[Permission], int]:
        try:
            query_filter: Dict[str, Any] = {}
            if search:
                query_filter["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                ]

            query = PermissionDocument.find(query_filter, session=session)
            return await paginate(query, page, limit, PermissionDocument.to_domain)
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_permission_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Permission:
        try:
            doc = await PermissionDocument.get(to_object_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(f"Permission '{id}' not found")

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
        except DuplicateKeyError as e:
            raise DuplicateDomainException(
                f"Permission name '{name}' already exists"
            ) from e
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_permission_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Permission:
        try:
            doc = await PermissionDocument.get(to_object_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(f"Permission '{id}' not found")

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

    async def delete_permission_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> None:
        try:
            permission_id = to_object_id(id)
            doc = await PermissionDocument.get(permission_id, session=session)
            if not doc:
                raise NotFoundDomainException(f"Permission '{id}' not found")

            role = await RoleDocument.find_one(
                {"permissions.$id": permission_id},
                session=session,
            )
            if role:
                raise ForbiddenDomainException("Permission is used by a role.")

            await doc.delete(session=session)
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e
