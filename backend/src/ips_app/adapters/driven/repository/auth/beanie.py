from typing import Optional, List, Tuple, Any, Dict
from ips_app.domain.models.auth import Auth
from ips_app.domain.models.user import User
from ips_app.ports.driven.repository.auth import AuthRepositoryPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.domain.models.exception import NotFoundException, DuplicateException
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone

class BeanieAuthRepository(AuthRepositoryPort):
    def __init__(self, log: GenericLoggingPort):
        self.log = log
        self.tag_class = "BeanieAuthRepository"

    async def create_auth(
        self, 
        user_id: Any, 
        username: str, 
        password_hash: str, 
        created_by: Optional[int] = None
    ) -> Auth:
        tag = f"{self.tag_class}.create_auth"
        try:
            auth = Auth(
                user=user_id, 
                username=username, 
                password_hash=password_hash, 
                created_by=created_by
            )
            await auth.insert()
            return auth
        except DuplicateKeyError as e:
            error_msg = str(e)
            field = "username" if "username" in error_msg else "unknown"
            
            await self.log.error(tag, f"Duplicate auth {field}", {"error": error_msg, "username": username})
            raise DuplicateException(field, "auths")
        except Exception as e:
            await self.log.error(tag, "Failed to create auth", {"error": str(e)})
            raise e

    async def read_auths_by_pagination(
        self, 
        page: int, 
        limit: int, 
        cursor_id: Optional[Any] = None, 
        search: Optional[str] = None
    ) -> Tuple[List[Auth], int]:
        tag = f"{self.tag_class}.read_auths_by_pagination"
        try:
            query_filter = {}
            if search:
                query_filter["username"] = {"$regex": search, "$options": "i"}
            
            if cursor_id:
                query_filter["_id"] = {"$gt": cursor_id}
            
            query = Auth.find(query_filter, fetch_links=True)
            total = await query.count()
            items = await query.skip(page * limit).limit(limit).to_list()
            return items, total
        except Exception as e:
            await self.log.error(tag, "Failed to read auths by pagination", {"error": str(e)})
            raise e

    async def read_auth_by_id(self, id: Any) -> Optional[Auth]:
        tag = f"{self.tag_class}.read_auth_by_id"
        try:
            return await Auth.get(id, fetch_links=True)
        except Exception as e:
            await self.log.error(tag, "Failed to read auth by id", {"error": str(e), "id": str(id)})
            raise e

    async def read_auth_by_user_id(self, user_id: Any) -> Optional[Auth]:
        tag = f"{self.tag_class}.read_auth_by_user_id"
        try:
            return await Auth.find_one({"user.$id": user_id}, fetch_links=True)
        except Exception as e:
            await self.log.error(tag, "Failed to read auth by user id", {"error": str(e), "user_id": str(user_id)})
            raise e

    async def read_auth_by_sign_in_identifier(self, sign_in_identifier: str) -> Optional[Auth]:
        tag = f"{self.tag_class}.read_auth_by_sign_in_identifier"
        try:
            return await Auth.find_one({"username": sign_in_identifier}, fetch_links=True)
        except Exception as e:
            await self.log.error(tag, "Failed to read auth by identifier", {"error": str(e), "identifier": sign_in_identifier})
            raise e

    async def update_auth_info_by_id(
        self, 
        id: Any, 
        username: Optional[str] = None, 
        updated_by: Optional[int] = None
    ) -> None:
        tag = f"{self.tag_class}.update_auth_info_by_id"
        try:
            auth = await Auth.get(id)
            if not auth:
                raise NotFoundException(str(id), "auths")
            
            update_data = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": auth.version + 1
            }
            if username is not None:
                update_data["username"] = username
            
            await auth.set(update_data)
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate username on update", {"error": str(e), "id": str(id)})
            raise DuplicateException("username", "auths")
        except NotFoundException:
            raise
        except Exception as e:
            await self.log.error(tag, "Failed to update auth info", {"error": str(e), "id": str(id)})
            raise e

    async def update_auth_password_by_id(
        self, 
        id: Any, 
        password_hash: str, 
        updated_by: Optional[int] = None
    ) -> None:
        tag = f"{self.tag_class}.update_auth_password_by_id"
        try:
            auth = await Auth.get(id)
            if not auth:
                raise NotFoundException(str(id), "auths")
            
            await auth.set({
                "password_hash": password_hash,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": auth.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to update auth password", {"error": str(e), "id": str(id)})
            raise e

    async def delete_auth_by_user_id(self, user_id: Any) -> None:
        tag = f"{self.tag_class}.delete_auth_by_user_id"
        try:
            auth = await Auth.find_one({"user.$id": user_id})
            if not auth:
                raise NotFoundException(str(user_id), "auths")
            await auth.delete()
        except Exception as e:
            await self.log.error(tag, "Failed to delete auth", {"error": str(e), "user_id": str(user_id)})
            raise e
