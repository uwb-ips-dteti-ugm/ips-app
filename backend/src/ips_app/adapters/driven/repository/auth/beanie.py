from typing import Optional, List, Tuple, Any, Dict
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from beanie import PydanticObjectId
from ips_app.domain.models.auth import Auth
from ips_app.domain.models.user import User
from ips_app.ports.driven.repository.auth import AuthRepositoryPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.domain.models.exception import NotFoundException, DuplicateException
from ips_app.adapters.driven.repository.auth.beanie_model import AuthDocument
from ips_app.adapters.driven.repository.user.beanie_model import UserDocument


class BeanieAuthRepository(AuthRepositoryPort):
    def __init__(self, log: GenericLoggingPort):
        self.log = log
        self.tag_class = "BeanieAuthRepository"

    def _to_obj_id(self, id_val: Any) -> Any:
        if isinstance(id_val, str) and PydanticObjectId.is_valid(id_val):
            return PydanticObjectId(id_val)
        return id_val

    async def create_auth(
        self,
        user_id: Any,
        username: str,
        password_hash: str,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> Auth:
        tag = f"{self.tag_class}.create_auth"
        session = kwargs.get("session")
        try:
            user_id = self._to_obj_id(user_id)
            
            # Using UserDocument instance ensures Beanie stores it as a DBRef
            user_doc = UserDocument(id=user_id) # type: ignore
            
            doc = AuthDocument(
                user=user_doc, # type: ignore
                username=username,
                password_hash=password_hash,
                created_by=created_by,
            )
            await doc.insert(session=session)
            return doc.to_domain()
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
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List[Auth], List[User], int]:
        tag = f"{self.tag_class}.read_auths_by_pagination"
        session = kwargs.get("session")
        try:
            match_filter: Dict[str, Any] = {}
            if cursor_id:
                match_filter["_id"] = {"$gt": self._to_obj_id(cursor_id)}
            
            search_filter: Dict[str, Any] = {}
            if search:
                search_filter = {
                    "$or": [
                        {"username": {"$regex": search, "$options": "i"}},
                        {"user_data.name": {"$regex": search, "$options": "i"}}
                    ]
                }

            pipeline = [
                {"$match": match_filter},
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "user.$id",
                        "foreignField": "_id",
                        "as": "user_data"
                    }
                },
                {"$unwind": "$user_data"},
                {"$match": search_filter},
            ]

            count_pipeline = pipeline + [{"$count": "total"}]
            count_result = await AuthDocument.aggregate(count_pipeline, session=session).to_list()
            total = count_result[0]["total"] if count_result else 0

            data_pipeline = pipeline + [
                {"$skip": page * limit},
                {"$limit": limit}
            ]
            
            results = await AuthDocument.aggregate(data_pipeline, session=session).to_list()
            
            auths: List[Auth] = []
            users: List[User] = []
            
            for res in results:
                user_data = res["user_data"]
                # Pass relationship keys explicitly to constructor if they are dicts
                user_doc = UserDocument(
                    role=user_data.get("role"), # type: ignore
                    **{k: v for k, v in user_data.items() if k not in ["_id", "role"]}
                )
                user_doc.id = user_data["_id"]
                
                res_auth = {k: v for k, v in res.items() if k not in ["user_data", "_id", "user"]}
                auth_doc = AuthDocument(user=user_doc, **res_auth) # type: ignore
                auth_doc.id = res["_id"]
                
                auths.append(auth_doc.to_domain())
                users.append(user_doc.to_domain())
                
            return auths, users, total
        except Exception as e:
            await self.log.error(tag, "Failed to read auths and users by pagination", {"error": str(e)})
            raise e

    async def read_auth_by_id(self, id: Any, **kwargs: Any) -> Optional[Auth]:
        tag = f"{self.tag_class}.read_auth_by_id"
        session = kwargs.get("session")
        try:
            doc = await AuthDocument.get(self._to_obj_id(id), fetch_links=True, session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read auth by id", {"error": str(e), "id": str(id)})
            raise e

    async def read_auth_by_user_id(self, user_id: Any, **kwargs: Any) -> Optional[Auth]:
        tag = f"{self.tag_class}.read_auth_by_user_id"
        session = kwargs.get("session")
        try:
            user_id_obj = self._to_obj_id(user_id)
            # Use Beanie fluent API which is designed for Link queries
            doc = await AuthDocument.find_one(AuthDocument.user.id == user_id_obj, fetch_links=True, session=session) # type: ignore
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read auth by user id", {"error": str(e), "user_id": str(user_id)})
            raise e

    async def read_auth_by_sign_in_identifier(
        self,
        sign_in_identifier: str,
        **kwargs: Any,
    ) -> Optional[Auth]:
        tag = f"{self.tag_class}.read_auth_by_sign_in_identifier"
        session = kwargs.get("session")
        try:
            doc = await AuthDocument.find_one({"username": sign_in_identifier}, fetch_links=True, session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read auth by identifier", {"error": str(e), "identifier": sign_in_identifier})
            raise e

    async def update_auth_info_by_id(self, id: Any, username: Optional[str] = None, updated_by: Optional[int] = None, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.update_auth_info_by_id"
        session = kwargs.get("session")
        try:
            doc = await AuthDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundException(str(id), "auths")

            update_data = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }
            if username is not None:
                update_data["username"] = username

            await doc.set(update_data, session=session)
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate username on update", {"error": str(e), "id": str(id)})
            raise DuplicateException("username", "auths")
        except NotFoundException:
            raise
        except Exception as e:
            await self.log.error(tag, "Failed to update auth info", {"error": str(e), "id": str(id)})
            raise e

    async def update_auth_password_by_id(self, id: Any, password_hash: str, updated_by: Optional[int] = None, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.update_auth_password_by_id"
        session = kwargs.get("session")
        try:
            doc = await AuthDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundException(str(id), "auths")

            await doc.set({
                "password_hash": password_hash,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update auth password", {"error": str(e), "id": str(id)})
            raise e

    async def delete_auth_by_user_id(self, user_id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_auth_by_user_id"
        session = kwargs.get("session")
        try:
            user_id_obj = self._to_obj_id(user_id)
            doc = await AuthDocument.find_one(AuthDocument.user.id == user_id_obj, session=session) # type: ignore
            if not doc:
                raise NotFoundException(str(user_id), "auths")
            await doc.delete(session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to delete auth", {"error": str(e), "user_id": str(user_id)})
            raise e
