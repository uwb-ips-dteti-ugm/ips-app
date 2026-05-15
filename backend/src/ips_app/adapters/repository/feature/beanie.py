from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from beanie import PydanticObjectId
from beanie.operators import In
from pymongo.errors import DuplicateKeyError

from ips_app.adapters.repository.feature.beanie_model import FeatureDocument
from ips_app.adapters.repository.permission.beanie_model import PermissionDocument
from ips_app.domain.models.exception import (
    DuplicateDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.feature import Feature
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.repository.feature import FeatureRepository


class BeanieFeatureRepository(FeatureRepository):
    def __init__(self, log: GenericLogging):
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_feature(
        self,
        name: str,
        description: str,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> Feature:
        tag = f"{self.tag_class}.create_feature"
        session = kwargs.get("session")
        try:
            doc = FeatureDocument(
                name=name,
                description=description,
                created_by=created_by,
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            await self.log.error(
                tag,
                "Duplicate feature name",
                {"error": str(e), "name": name},
            )
            raise DuplicateDomainException("name", "features")
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to create feature",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_feature_by_id(self, id: Any, **kwargs: Any) -> Feature:
        tag = f"{self.tag_class}.read_feature_by_id"
        session = kwargs.get("session")
        try:
            doc = await FeatureDocument.get(
                self._to_obj_id(id),
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(str(id), "features")
            return doc.to_domain()
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read feature by id",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_feature_by_name(self, name: str, **kwargs: Any) -> Feature:
        tag = f"{self.tag_class}.read_feature_by_name"
        session = kwargs.get("session")
        try:
            doc = await FeatureDocument.find_one(
                {"name": name},
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(name, "features")
            return doc.to_domain()
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read feature by name",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_features_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List[Feature], int]:
        tag = f"{self.tag_class}.read_features_by_pagination"
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

            query = FeatureDocument.find(query_filter, fetch_links=True, session=session)
            total = await query.count()
            query = query.sort("_id")
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read features by pagination",
                {"error": str(e), "page": page, "limit": limit},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_feature_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_feature_by_id"
        session = kwargs.get("session")
        try:
            doc = await FeatureDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(str(id), "features")

            update_data: Dict[str, Any] = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description

            await doc.set(update_data, session=session)
        except DuplicateKeyError as e:
            await self.log.error(
                tag,
                "Duplicate feature name on update",
                {"error": str(e), "id": str(id), "name": name},
            )
            raise DuplicateDomainException("name", "features")
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update feature",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_feature_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_feature_preferences_by_id"
        session = kwargs.get("session")
        try:
            doc = await FeatureDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(str(id), "features")

            now = datetime.now(timezone.utc)
            await doc.set(
                {
                    "preferences": preferences,
                    "updated_at": now,
                    "updated_by": updated_by,
                    "version": doc.version + 1,
                },
                session=session,
            )
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update feature preferences",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def delete_feature_by_id(self, id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_feature_by_id"
        session = kwargs.get("session")
        try:
            doc = await FeatureDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(str(id), "features")
            await doc.delete(session=session)
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to delete feature",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def add_permissions_to_feature(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.add_permissions_to_feature"
        session = kwargs.get("session")
        try:
            doc = await FeatureDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(str(id), "features")

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
                doc.version += 1
                await doc.save(session=session)
                await self.log.info(
                    tag,
                    "Added permissions to feature",
                    {"id": str(id), "count": added_count},
                )
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add permissions to feature",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_permissions_from_feature(
        self,
        id: Any,
        permission_ids: List[Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.remove_permissions_from_feature"
        session = kwargs.get("session")
        try:
            doc = await FeatureDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundDomainException(str(id), "features")

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
                doc.version += 1
                await doc.save(session=session)
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove permissions from feature",
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
