from typing import Optional, List, Tuple, Any, Dict
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from beanie import PydanticObjectId
from ips_app_old.domain.models.user import User, UserState, UserStatus
from ips_app_old.ports.driven.repository.user import UserRepository
from ips_app_old.ports.driven.logging.generic import GenericLoggingPort
from ips_app_old.domain.models.exception import NotFoundException, DuplicateException
from ips_app_old.adapters.driven.repository.user.beanie_model import UserDocument


class BeanieUserRepository(UserRepository):
    def __init__(self, log: GenericLoggingPort):
        self.log = log
        self.tag_class = "BeanieUserRepository"

    async def create_user(
        self,
        role_id: Any,
        name: str,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> User:
        tag = f"{self.tag_class}.create_user"
        session = kwargs.get("session")
        try:
            doc = UserDocument(role=role_id, name=name, created_by=created_by)
            await doc.insert(session=session)
            return doc.to_domain()
        except Exception as e:
            await self.log.error(tag, "Failed to create user", {"error": str(e)})
            raise e

    async def read_user_by_id(self, id: Any, **kwargs: Any) -> Optional[User]:
        tag = f"{self.tag_class}.read_user_by_id"
        session = kwargs.get("session")
        try:
            doc = await UserDocument.get(id, fetch_links=True, session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read user by id", {"error": str(e), "id": str(id)})
            raise e

    async def read_users_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        role_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> Tuple[List[User], int]:
        tag = f"{self.tag_class}.read_users_by_pagination"
        session = kwargs.get("session")
        try:
            query_filter: Dict[str, Any] = {}
            if search:
                query_filter["name"] = {"$regex": search, "$options": "i"}
            if role_id:
                if isinstance(role_id, str) and PydanticObjectId.is_valid(role_id):
                    role_id = PydanticObjectId(role_id)
                query_filter["role.$id"] = role_id
            if cursor_id:
                if isinstance(cursor_id, str) and PydanticObjectId.is_valid(cursor_id):
                    cursor_id = PydanticObjectId(cursor_id)
                query_filter["_id"] = {"$gt": cursor_id}

            query = UserDocument.find(query_filter, fetch_links=True, session=session)
            total = await query.count()
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except Exception as e:
            await self.log.error(tag, "Failed to read users by pagination", {"error": str(e)})
            raise e

    async def update_user_info_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_info_by_id"
        session = kwargs.get("session")
        try:
            doc = await UserDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "users")

            update_data: Dict[str, Any] = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }
            if name is not None:
                update_data["name"] = name
            if bio is not None:
                update_data["bio"] = bio

            await doc.set(update_data, session=session)
        except NotFoundException:
            raise
        except Exception as e:
            await self.log.error(tag, "Failed to update user info", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_state_by_id(
        self,
        id: Any,
        state: UserState,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_state_by_id"
        session = kwargs.get("session")
        try:
            doc = await UserDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "users")
            await doc.set({
                "state": state,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update user state", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_status_by_id(
        self,
        id: Any,
        status: UserStatus,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_status_by_id"
        session = kwargs.get("session")
        try:
            doc = await UserDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "users")
            await doc.set({
                "status": status,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update user status", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_role_by_id(
        self,
        id: Any,
        role_id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_role_by_id"
        session = kwargs.get("session")
        try:
            doc = await UserDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "users")
            await doc.set({
                "role": role_id,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update user role", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_preferences_by_id"
        session = kwargs.get("session")
        try:
            doc = await UserDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "users")
            await doc.set({
                "preferences": preferences,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update user preferences", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_last_signed_in_at_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_last_signed_in_at_by_id"
        session = kwargs.get("session")
        try:
            doc = await UserDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "users")
            now = datetime.now(timezone.utc)
            await doc.set({
                "last_signed_in_at": now,
                "updated_at": now,
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update last signed in", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_last_refreshed_at_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_last_refreshed_at_by_id"
        session = kwargs.get("session")
        try:
            doc = await UserDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "users")
            now = datetime.now(timezone.utc)
            await doc.set({
                "last_refreshed_at": now,
                "updated_at": now,
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update last refreshed", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_last_activity_at_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_last_activity_at_by_id"
        session = kwargs.get("session")
        try:
            doc = await UserDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "users")
            now = datetime.now(timezone.utc)
            await doc.set({
                "last_activity_at": now,
                "updated_at": now,
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update last activity", {"error": str(e), "id": str(id)})
            raise e

    async def delete_user_by_id(self, id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_user_by_id"
        session = kwargs.get("session")
        try:
            doc = await UserDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "users")
            await doc.delete(session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to delete user", {"error": str(e), "id": str(id)})
            raise e
