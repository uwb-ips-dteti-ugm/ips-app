import json
from typing import Optional, List, Tuple, Any
from ips_app.domain.models.user import User, UserState, UserStatus
from ips_app.ports.driving.http.user import UserHTTPPort
from ips_app.ports.driven.repository.user import UserRepositoryPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.domain.models.exception import NotFoundException

class UserHTTPService(UserHTTPPort):
    def __init__(self, repo: UserRepositoryPort, log: GenericLoggingPort):
        self.repo = repo
        self.log = log
        self.tag_class = "UserHTTPService"

    async def get_user(self, user_id: Any) -> User:
        tag = f"{self.tag_class}.get_user"
        try:
            user = await self.repo.read_user_by_id(user_id)
            if not user:
                raise NotFoundException(str(user_id), "users")
            return user
        except Exception as e:
            await self.log.error(tag, "Failed to get user", {"error": str(e), "id": str(user_id)})
            raise e

    async def get_users(
        self, 
        page: int, 
        limit: int, 
        cursor_id: Optional[Any] = None, 
        search: Optional[str] = None, 
        role_id: Optional[Any] = None
    ) -> Tuple[List[User], int]:
        tag = f"{self.tag_class}.get_users"
        try:
            return await self.repo.read_users_by_pagination(page, limit, cursor_id, search, role_id)
        except Exception as e:
            await self.log.error(tag, "Failed to get users", {"error": str(e), "page": page, "limit": limit})
            raise e

    async def set_user_info(
        self, 
        user_id: Any, 
        name: Optional[str] = None, 
        bio: Optional[str] = None
    ) -> User:
        tag = f"{self.tag_class}.set_user_info"
        try:
            await self.repo.update_user_info_by_id(user_id, name, bio)
            user = await self.get_user(user_id)
            await self.log.info(tag, "Successfully updated user info", {"id": str(user_id)})
            return user
        except Exception as e:
            await self.log.error(tag, "Failed to set user info", {"error": str(e), "id": str(user_id)})
            raise e

    async def set_user_preferences(self, user_id: Any, preferences: bytes) -> User:
        tag = f"{self.tag_class}.set_user_preferences"
        try:
            prefs_dict = json.loads(preferences)
            await self.repo.update_user_preferences_by_id(user_id, prefs_dict)
            user = await self.get_user(user_id)
            await self.log.info(tag, "Successfully updated user preferences", {"id": str(user_id)})
            return user
        except Exception as e:
            await self.log.error(tag, "Failed to set user preferences", {"error": str(e), "id": str(user_id)})
            raise e

    async def set_user_role(self, user_id: Any, role_id: Any) -> User:
        tag = f"{self.tag_class}.set_user_role"
        try:
            await self.repo.update_user_role_by_id(user_id, role_id)
            user = await self.get_user(user_id)
            await self.log.info(tag, "Successfully updated user role", {"id": str(user_id), "role_id": str(role_id)})
            return user
        except Exception as e:
            await self.log.error(tag, "Failed to set user role", {"error": str(e), "id": str(user_id)})
            raise e

    async def set_user_state(self, user_id: Any, state: UserState) -> User:
        tag = f"{self.tag_class}.set_user_state"
        try:
            await self.repo.update_user_state_by_id(user_id, state)
            user = await self.get_user(user_id)
            await self.log.info(tag, "Successfully updated user state", {"id": str(user_id), "state": state})
            return user
        except Exception as e:
            await self.log.error(tag, "Failed to set user state", {"error": str(e), "id": str(user_id)})
            raise e

    async def set_user_status(self, user_id: Any, status: UserStatus) -> User:
        tag = f"{self.tag_class}.set_user_status"
        try:
            await self.repo.update_user_status_by_id(user_id, status)
            user = await self.get_user(user_id)
            await self.log.info(tag, "Successfully updated user status", {"id": str(user_id), "status": status})
            return user
        except Exception as e:
            await self.log.error(tag, "Failed to set user status", {"error": str(e), "id": str(user_id)})
            raise e

    async def remove_user(self, user_id: Any) -> str:
        tag = f"{self.tag_class}.remove_user"
        try:
            await self.repo.delete_user_by_id(user_id)
            await self.log.info(tag, "Successfully removed user", {"id": str(user_id)})
            return "User removed successfully"
        except Exception as e:
            await self.log.error(tag, "Failed to remove user", {"error": str(e), "id": str(user_id)})
            raise e
