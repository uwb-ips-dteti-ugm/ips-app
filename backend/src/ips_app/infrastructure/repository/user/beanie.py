from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, cast

from beanie import Link
from pymongo.errors import DuplicateKeyError

from ips_app.domain.contracts.repository.user import UserRepository
from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.permission import Permission
from ips_app.domain.models.user import User, UserStatus
from ips_app.infrastructure.repository._shared.link import link_id
from ips_app.infrastructure.repository._shared.object_id import get_by_id, to_object_id
from ips_app.infrastructure.repository._shared.pagination import paginate_with_links
from ips_app.infrastructure.repository.role.beanie_model import RoleDocument
from ips_app.infrastructure.repository.user.beanie_model import UserDocument


class BeanieUserRepository(UserRepository):
    async def create_user(
        self,
        role_id: Any,
        name: str,
        username: str,
        password_hash: str,
        bio: str = "",
        created_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User:
        try:
            role = await self._read_role_document(role_id, session)
            doc = UserDocument(
                role=cast(Link[RoleDocument], role),
                name=name,
                username=username,
                password_hash=password_hash,
                bio=bio,
                created_by=created_by,
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            raise DuplicateDomainException(
                f"Username '{username}' already exists"
            ) from e
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_user_by_id(self, id: Any, session: Optional[Any] = None) -> User:
        try:
            doc = await self._read_user_document(id, session, fetch_links=True)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_user_by_username(
        self,
        username: str,
        session: Optional[Any] = None,
    ) -> User:
        try:
            doc = await UserDocument.find_one(
                {"username": username},
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(f"User '{username}' not found")
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_users_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        role_id: Optional[Any] = None,
        status: Optional[UserStatus] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[User], int]:
        try:
            query_filter: Dict[str, Any] = {}
            if search:
                query_filter["name"] = {"$regex": search, "$options": "i"}
            if role_id:
                query_filter["role.$id"] = to_object_id(role_id)
            if status:
                query_filter["status"] = status.value

            return await paginate_with_links(
                UserDocument,
                query_filter,
                page,
                limit,
                UserDocument.to_domain,
                session=session,
            )
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_user_permissions_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> List[Permission]:
        try:
            user = await self._read_user_document(id, session, fetch_links=True)
            role_id = link_id(user.role)
            role = await get_by_id(RoleDocument, role_id, fetch_links=True, session=session)
            if not role:
                raise NotFoundDomainException(f"Role '{role_id}' not found")
            return role.to_domain().permissions
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        username: Optional[str] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User:
        try:
            doc = await self._read_user_document(id, session, fetch_links=True)
            update_data: Dict[str, Any] = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
            }
            if name is not None:
                update_data["name"] = name
            if bio is not None:
                update_data["bio"] = bio
            if username is not None:
                update_data["username"] = username

            await doc.set(update_data, session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            raise DuplicateDomainException(
                f"Username '{username}' already exists"
            ) from e
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_password_by_id(
        self,
        id: Any,
        password_hash: str,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User:
        try:
            doc = await self._read_user_document(id, session, fetch_links=True)
            await doc.set(
                {
                    "password_hash": password_hash,
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

    async def update_user_status_by_id(
        self,
        id: Any,
        status: UserStatus,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User:
        try:
            doc = await self._read_user_document(id, session, fetch_links=True)
            await doc.set(
                {
                    "status": status,
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

    async def update_user_role_by_id(
        self,
        id: Any,
        role_id: Any,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User:
        try:
            doc = await self._read_user_document(id, session, fetch_links=True)
            role = await self._read_role_document(role_id, session)
            await doc.set(
                {
                    "role": role,
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": updated_by,
                },
                session=session,
            )
            doc.role = cast(Link[RoleDocument], role)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> User:
        try:
            doc = await self._read_user_document(id, session, fetch_links=True)
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

    async def delete_user_by_id(self, id: Any, session: Optional[Any] = None) -> None:
        try:
            doc = await self._read_user_document(id, session)
            await doc.delete(session=session)
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def _read_user_document(
        self,
        id: Any,
        session: Optional[Any],
        fetch_links: bool = False,
    ) -> UserDocument:
        doc = await get_by_id(UserDocument, id, fetch_links=fetch_links, session=session)
        if not doc:
            raise NotFoundDomainException(f"User '{id}' not found")
        return doc

    async def _read_role_document(
        self,
        role_id: Any,
        session: Optional[Any],
    ) -> RoleDocument:
        role = await get_by_id(RoleDocument, role_id, fetch_links=True, session=session)
        if not role:
            raise NotFoundDomainException(f"Role '{role_id}' not found")
        return role
