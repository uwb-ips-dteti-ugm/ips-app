from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, cast

from beanie import Link, PydanticObjectId
from pydantic import TypeAdapter
from pymongo.errors import DuplicateKeyError

from ips_app.adapters.repository.role.beanie_model import RoleDocument
from ips_app.adapters.repository.user.beanie_model import UserDocument
from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.user import (
    User,
    UserAuth,
    UserAuthType,
    UserPasswordAuth,
    UserState,
    UserStatus,
)
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.repository.user import UserRepository


class BeanieUserRepository(UserRepository):
    def __init__(self, log: GenericLogging):
        self.log = log
        self.tag_class = self.__class__.__name__
        self.auth_adapter = TypeAdapter(UserAuth)

    async def create_user(
        self,
        role_id: Any,
        name: str,
        auths: Optional[List[UserAuth]] = None,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> User:
        tag = f"{self.tag_class}.create_user"
        session = kwargs.get("session")
        try:
            role = await self._read_role_document(role_id, session)
            doc = UserDocument(
                role=cast(Optional[Link[RoleDocument]], role),
                name=name,
                auths=self._normalize_auths(auths),
                created_by=created_by,
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            field = self._duplicate_field(e)
            await self.log.error(
                tag,
                "Duplicate user auth",
                {"error": str(e), "field": field, "name": name},
            )
            raise DuplicateDomainException(field, "users")
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to create user",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_user_by_id(self, id: Any, **kwargs: Any) -> User:
        tag = f"{self.tag_class}.read_user_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_user_document(id, session, fetch_links=True)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read user by id",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_user_by_username(
        self,
        username: str,
        **kwargs: Any,
    ) -> User:
        tag = f"{self.tag_class}.read_user_by_username"
        session = kwargs.get("session")
        try:
            doc = await UserDocument.find_one(
                {
                    "auths": {
                        "$elemMatch": {
                            "type": UserAuthType.PASSWORD.value,
                            "username": username,
                        },
                    },
                },
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(username, "users")
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read user by username",
                {"error": str(e), "username": username},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_users_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        role_id: Optional[Any] = None,
        state: Optional[UserState] = None,
        status: Optional[UserStatus] = None,
        **kwargs: Any,
    ) -> Tuple[List[User], int]:
        tag = f"{self.tag_class}.read_users_by_pagination"
        session = kwargs.get("session")
        try:
            query_filter: Dict[str, Any] = {}
            if cursor_id:
                query_filter["_id"] = {"$gt": self._to_obj_id(cursor_id)}
            if search:
                query_filter["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"auths.username": {"$regex": search, "$options": "i"}},
                ]
            if role_id:
                query_filter["role.$id"] = self._to_obj_id(role_id)
            if state:
                query_filter["state"] = state.value
            if status:
                query_filter["status"] = status.value

            query = UserDocument.find(query_filter, fetch_links=True, session=session)
            total = await query.count()
            query = query.sort("_id")
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read users by pagination",
                {
                    "error": str(e),
                    "page": page,
                    "limit": limit,
                    "state": str(state) if state else None,
                    "status": str(status) if status else None,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def add_user_auth_by_id(
        self,
        id: Any,
        auth: UserAuth,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.add_user_auth_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_user_document(id, session)
            normalized_auth = self.auth_adapter.validate_python(auth)
            if any(existing_auth.type == normalized_auth.type for existing_auth in doc.auths):
                raise DuplicateDomainException("auths.type", "users")

            doc.auths.append(normalized_auth)
            doc.updated_at = datetime.now(timezone.utc)
            doc.updated_by = updated_by
            doc.version += 1
            await doc.save(session=session)
        except DuplicateKeyError as e:
            field = self._duplicate_field(e)
            await self.log.error(
                tag,
                "Duplicate user auth",
                {"error": str(e), "field": field, "id": str(id)},
            )
            raise DuplicateDomainException(field, "users")
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add user auth",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_password_auth_info_by_id(
        self,
        id: Any,
        username: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_password_auth_info_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_user_document(id, session)
            index = self._password_auth_index(doc)
            auth = doc.auths[index]
            if not isinstance(auth, UserPasswordAuth):
                raise NotFoundDomainException(UserAuthType.PASSWORD.value, "auths")

            now = datetime.now(timezone.utc)
            update_data: Dict[str, Any] = {
                "updated_at": now,
                "updated_by": updated_by,
            }
            if username is not None:
                update_data["username"] = username

            doc.auths[index] = auth.model_copy(update=update_data)
            doc.updated_at = now
            doc.updated_by = updated_by
            doc.version += 1
            await doc.save(session=session)
        except DuplicateKeyError as e:
            field = self._duplicate_field(e)
            await self.log.error(
                tag,
                "Duplicate user auth",
                {"error": str(e), "field": field, "id": str(id), "username": username},
            )
            raise DuplicateDomainException(field, "users")
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user password auth info",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_password_auth_password_by_id(
        self,
        id: Any,
        password_hash: str,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_password_auth_password_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_user_document(id, session)
            index = self._password_auth_index(doc)
            auth = doc.auths[index]
            if not isinstance(auth, UserPasswordAuth):
                raise NotFoundDomainException(UserAuthType.PASSWORD.value, "auths")

            now = datetime.now(timezone.utc)
            doc.auths[index] = auth.model_copy(
                update={
                    "password_hash": password_hash,
                    "updated_at": now,
                    "updated_by": updated_by,
                }
            )
            doc.updated_at = now
            doc.updated_by = updated_by
            doc.version += 1
            await doc.save(session=session)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user password auth password",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def delete_user_auth_by_id(
        self,
        id: Any,
        auth_type: UserAuthType,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.delete_user_auth_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_user_document(id, session)
            remaining_auths = [auth for auth in doc.auths if auth.type != auth_type]
            if len(remaining_auths) == len(doc.auths):
                raise NotFoundDomainException(str(auth_type), "auths")

            doc.auths = remaining_auths
            doc.updated_at = datetime.now(timezone.utc)
            doc.updated_by = updated_by
            doc.version += 1
            await doc.save(session=session)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to delete user auth",
                {"error": str(e), "id": str(id), "auth_type": str(auth_type)},
            )
            raise UnexpectedDomainException(str(e)) from e

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
            doc = await self._read_user_document(id, session)
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
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user info",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

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
            doc = await self._read_user_document(id, session)
            await doc.set(
                {
                    "state": state,
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": updated_by,
                    "version": doc.version + 1,
                },
                session=session,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user state",
                {"error": str(e), "id": str(id), "state": str(state)},
            )
            raise UnexpectedDomainException(str(e)) from e

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
            doc = await self._read_user_document(id, session)
            await doc.set(
                {
                    "status": status,
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": updated_by,
                    "version": doc.version + 1,
                },
                session=session,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user status",
                {"error": str(e), "id": str(id), "status": str(status)},
            )
            raise UnexpectedDomainException(str(e)) from e

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
            doc = await self._read_user_document(id, session)
            role = await self._read_role_document(role_id, session)
            await doc.set(
                {
                    "role": role,
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": updated_by,
                    "version": doc.version + 1,
                },
                session=session,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user role",
                {"error": str(e), "id": str(id), "role_id": str(role_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

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
            doc = await self._read_user_document(id, session)
            await doc.set(
                {
                    "preferences": preferences,
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": updated_by,
                    "version": doc.version + 1,
                },
                session=session,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user preferences",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_last_signed_in_at_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_last_signed_in_at_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_user_document(id, session)
            now = datetime.now(timezone.utc)
            await doc.set(
                {
                    "last_signed_in_at": now,
                    "updated_at": now,
                    "updated_by": updated_by,
                    "version": doc.version + 1,
                },
                session=session,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user last signed in",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_last_refreshed_at_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_last_refreshed_at_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_user_document(id, session)
            now = datetime.now(timezone.utc)
            await doc.set(
                {
                    "last_refreshed_at": now,
                    "updated_at": now,
                    "updated_by": updated_by,
                    "version": doc.version + 1,
                },
                session=session,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user last refreshed",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_user_last_activity_at_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_user_last_activity_at_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_user_document(id, session)
            now = datetime.now(timezone.utc)
            await doc.set(
                {
                    "last_activity_at": now,
                    "updated_at": now,
                    "updated_by": updated_by,
                    "version": doc.version + 1,
                },
                session=session,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user last activity",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_users_state_with_cutoffs(
        self,
        away_cutoff: datetime,
        offline_cutoff: datetime,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> Tuple[int, int]:
        tag = f"{self.tag_class}.update_users_state_with_cutoffs"
        session = kwargs.get("session")
        try:
            now = datetime.now(timezone.utc)
            collection = UserDocument.get_motor_collection()

            away_result = await collection.update_many(
                {
                    "last_activity_at": {
                        "$ne": None,
                        "$lt": away_cutoff,
                        "$gt": offline_cutoff,
                    },
                    "state": {
                        "$nin": [
                            UserState.AWAY.value,
                            UserState.DND.value,
                        ],
                    },
                },
                {
                    "$set": {
                        "state": UserState.AWAY.value,
                        "updated_at": now,
                        "updated_by": updated_by,
                    },
                    "$inc": {"version": 1},
                },
                session=session,
            )
            offline_result = await collection.update_many(
                {
                    "last_activity_at": {
                        "$ne": None,
                        "$lt": offline_cutoff,
                    },
                    "state": {
                        "$nin": [
                            UserState.OFFLINE.value,
                            UserState.DND.value,
                        ],
                    },
                },
                {
                    "$set": {
                        "state": UserState.OFFLINE.value,
                        "updated_at": now,
                        "updated_by": updated_by,
                    },
                    "$inc": {"version": 1},
                },
                session=session,
            )
            return away_result.modified_count, offline_result.modified_count
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user states with cutoffs",
                {
                    "error": str(e),
                    "away_cutoff": away_cutoff.isoformat(),
                    "offline_cutoff": offline_cutoff.isoformat(),
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def delete_user_by_id(self, id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_user_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_user_document(id, session)
            await doc.delete(session=session)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to delete user",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    def _to_obj_id(self, value: Any) -> Any:
        if isinstance(value, str) and PydanticObjectId.is_valid(value):
            return PydanticObjectId(value)
        return value

    def _duplicate_field(self, error: DuplicateKeyError) -> str:
        error_message = str(error)
        if "auths.username" in error_message or "username" in error_message:
            return "username"
        return "auth"

    async def _read_user_document(
        self,
        id: Any,
        session: Any,
        fetch_links: bool = False,
    ) -> UserDocument:
        doc = await UserDocument.get(
            self._to_obj_id(id),
            fetch_links=fetch_links,
            session=session,
        )
        if not doc:
            raise NotFoundDomainException(str(id), "users")
        return doc

    async def _read_role_document(
        self,
        role_id: Any,
        session: Any,
    ) -> Optional[RoleDocument]:
        if role_id is None:
            return None

        role = await RoleDocument.get(self._to_obj_id(role_id), session=session)
        if not role:
            raise NotFoundDomainException(str(role_id), "roles")
        return role

    def _normalize_auths(self, auths: Optional[List[UserAuth]]) -> List[UserAuth]:
        normalized = [self.auth_adapter.validate_python(auth) for auth in auths or []]
        seen_types: set[UserAuthType] = set()
        for auth in normalized:
            if auth.type in seen_types:
                raise DuplicateDomainException("auths.type", "users")
            seen_types.add(auth.type)
        return normalized

    def _password_auth_index(self, doc: UserDocument) -> int:
        for index, auth in enumerate(doc.auths):
            if isinstance(auth, UserPasswordAuth):
                return index
        raise NotFoundDomainException(UserAuthType.PASSWORD.value, "auths")
