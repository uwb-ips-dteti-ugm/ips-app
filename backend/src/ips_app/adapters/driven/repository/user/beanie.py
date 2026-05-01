from typing import Optional, List, Tuple, Any, Dict
from ips_app.domain.models.user import User, UserState, UserStatus
from ips_app.ports.driven.repository.user import UserRepositoryPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.domain.models.exception import NotFoundException, DuplicateException
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone

class BeanieUserRepository(UserRepositoryPort):
    def __init__(self, log: GenericLoggingPort):
        self.log = log
        self.tag_class = "BeanieUserRepository"

    async def create_user(
        self, 
        role_id: Any, 
        name: str, 
        created_by: Optional[int] = None
    ) -> User:
        tag = f"{self.tag_class}.create_user"
        try:
            user = User(role=role_id, name=name, created_by=created_by)
            await user.insert()
            return user
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate user name", {"error": str(e), "name": name})
            raise DuplicateException("name", "users")
        except Exception as e:
            await self.log.error(tag, "Failed to create user", {"error": str(e)})
            raise e

    async def read_user_by_id(self, id: Any) -> Optional[User]:
        tag = f"{self.tag_class}.read_user_by_id"
        try:
            return await User.get(id, fetch_links=True)
        except Exception as e:
            await self.log.error(tag, "Failed to read user by id", {"error": str(e), "id": str(id)})
            raise e

    async def read_users_by_pagination(
        self, 
        page: int, 
        limit: int, 
        cursor_id: Optional[Any] = None, 
        search: Optional[str] = None, 
        role_id: Optional[Any] = None
    ) -> Tuple[List[User], int]:
        tag = f"{self.tag_class}.read_users_by_pagination"
        try:
            query_filter = {}
            if search:
                query_filter["name"] = {"$regex": search, "$options": "i"}
            if role_id:
                query_filter["role.$id"] = role_id
            if cursor_id:
                query_filter["_id"] = {"$gt": cursor_id}
            
            query = User.find(query_filter, fetch_links=True)
            total = await query.count()
            items = await query.skip(page * limit).limit(limit).to_list()
            return items, total
        except Exception as e:
            await self.log.error(tag, "Failed to read users by pagination", {"error": str(e)})
            raise e

    async def update_user_info_by_id(
        self, 
        id: Any, 
        name: Optional[str] = None, 
        bio: Optional[str] = None, 
        updated_by: Optional[int] = None
    ) -> None:
        tag = f"{self.tag_class}.update_user_info_by_id"
        try:
            user = await User.get(id)
            if not user:
                raise NotFoundException(str(id), "users")
            
            update_data = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": user.version + 1
            }
            if name is not None:
                update_data["name"] = name
            if bio is not None:
                update_data["bio"] = bio
            
            await user.set(update_data)
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate user name on update", {"error": str(e), "id": str(id)})
            raise DuplicateException("name", "users")
        except NotFoundException:
            raise
        except Exception as e:
            await self.log.error(tag, "Failed to update user info", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_state_by_id(self, id: Any, state: UserState, updated_by: Optional[int] = None) -> None:
        tag = f"{self.tag_class}.update_user_state_by_id"
        try:
            user = await User.get(id)
            if not user:
                raise NotFoundException(str(id), "users")
            await user.set({
                "state": state,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": user.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to update user state", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_status_by_id(self, id: Any, status: UserStatus, updated_by: Optional[int] = None) -> None:
        tag = f"{self.tag_class}.update_user_status_by_id"
        try:
            user = await User.get(id)
            if not user:
                raise NotFoundException(str(id), "users")
            await user.set({
                "status": status,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": user.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to update user status", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_role_by_id(self, id: Any, role_id: Any, updated_by: Optional[int] = None) -> None:
        tag = f"{self.tag_class}.update_user_role_by_id"
        try:
            user = await User.get(id)
            if not user:
                raise NotFoundException(str(id), "users")
            await user.set({
                "role": role_id,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": user.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to update user role", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_preferences_by_id(
        self, 
        id: Any, 
        preferences: Dict[str, Any], 
        updated_by: Optional[int] = None
    ) -> None:
        tag = f"{self.tag_class}.update_user_preferences_by_id"
        try:
            user = await User.get(id)
            if not user:
                raise NotFoundException(str(id), "users")
            await user.set({
                "preferences": preferences,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": user.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to update user preferences", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_last_signed_in_at_by_id(self, id: Any, updated_by: Optional[int] = None) -> None:
        tag = f"{self.tag_class}.update_user_last_signed_in_at_by_id"
        try:
            user = await User.get(id)
            if not user:
                raise NotFoundException(str(id), "users")
            now = datetime.now(timezone.utc)
            await user.set({
                "last_signed_in_at": now,
                "updated_at": now,
                "updated_by": updated_by,
                "version": user.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to update last signed in", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_last_refreshed_at_by_id(self, id: Any, updated_by: Optional[int] = None) -> None:
        tag = f"{self.tag_class}.update_user_last_refreshed_at_by_id"
        try:
            user = await User.get(id)
            if not user:
                raise NotFoundException(str(id), "users")
            now = datetime.now(timezone.utc)
            await user.set({
                "last_refreshed_at": now,
                "updated_at": now,
                "updated_by": updated_by,
                "version": user.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to update last refreshed", {"error": str(e), "id": str(id)})
            raise e

    async def update_user_last_activity_at_by_id(self, id: Any, updated_by: Optional[int] = None) -> None:
        tag = f"{self.tag_class}.update_user_last_activity_at_by_id"
        try:
            user = await User.get(id)
            if not user:
                raise NotFoundException(str(id), "users")
            now = datetime.now(timezone.utc)
            await user.set({
                "last_activity_at": now,
                "updated_at": now,
                "updated_by": updated_by,
                "version": user.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to update last activity", {"error": str(e), "id": str(id)})
            raise e

    async def delete_user_by_id(self, id: Any) -> None:
        tag = f"{self.tag_class}.delete_user_by_id"
        try:
            user = await User.get(id)
            if not user:
                raise NotFoundException(str(id), "users")
            await user.delete()
        except Exception as e:
            await self.log.error(tag, "Failed to delete user", {"error": str(e), "id": str(id)})
            raise e
