from typing import Optional, List, Tuple, Any, Dict
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from beanie.operators import In
from beanie import PydanticObjectId
from ips_app_old.domain.models.feature import Feature
from ips_app_old.ports.driven.repository.feature import FeatureRepository
from ips_app_old.ports.driven.logging.generic import GenericLoggingPort
from ips_app_old.domain.models.exception import NotFoundException, DuplicateException
from ips_app_old.adapters.driven.repository.feature.beanie_model import FeatureDocument
from ips_app_old.adapters.driven.repository.permission.beanie_model import PermissionDocument


class BeanieFeatureRepository(FeatureRepository):
    def __init__(self, log: GenericLoggingPort):
        self.log = log
        self.tag_class = "BeanieFeatureRepository"

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
            doc = FeatureDocument(name=name, description=description, created_by=created_by)
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate feature name", {"error": str(e), "name": name})
            raise DuplicateException("name", "features")
        except Exception as e:
            await self.log.error(tag, "Failed to create feature", {"error": str(e)})
            raise e

    async def read_feature_by_id(self, id: Any, **kwargs: Any) -> Optional[Feature]:
        tag = f"{self.tag_class}.read_feature_by_id"
        session = kwargs.get("session")
        try:
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await FeatureDocument.get(id, fetch_links=True, session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read feature by id", {"error": str(e), "id": str(id)})
            raise e

    async def read_feature_by_name(self, name: str, **kwargs: Any) -> Optional[Feature]:
        tag = f"{self.tag_class}.read_feature_by_name"
        session = kwargs.get("session")
        try:
            doc = await FeatureDocument.find_one({"name": name}, fetch_links=True, session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read feature by name", {"error": str(e), "name": name})
            raise e

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
            query = FeatureDocument.find_all(session=session)
            if search:
                query = FeatureDocument.find({"name": {"$regex": search, "$options": "i"}}, session=session)
            if cursor_id:
                if isinstance(cursor_id, str) and PydanticObjectId.is_valid(cursor_id):
                    cursor_id = PydanticObjectId(cursor_id)
                query = query.find({"_id": {"$gt": cursor_id}})

            total = await query.count()
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except Exception as e:
            await self.log.error(tag, "Failed to read features by pagination", {"error": str(e)})
            raise e

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
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await FeatureDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "features")

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
            await self.log.error(tag, "Duplicate feature name on update", {"error": str(e), "id": str(id)})
            raise DuplicateException("name", "features")
        except NotFoundException:
            raise
        except Exception as e:
            await self.log.error(tag, "Failed to update feature", {"error": str(e), "id": str(id)})
            raise e

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
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await FeatureDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "features")

            await doc.set({
                "preferences": preferences,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update feature preferences", {"error": str(e), "id": str(id)})
            raise e

    async def delete_feature_by_id(self, id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_feature_by_id"
        session = kwargs.get("session")
        try:
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await FeatureDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "features")
            await doc.delete(session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to delete feature", {"error": str(e), "id": str(id)})
            raise e

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
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await FeatureDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "features")

            # Convert permission_ids to ObjectIds for the query
            valid_ids = [PydanticObjectId(pid) if isinstance(pid, str) and PydanticObjectId.is_valid(pid) else pid for pid in permission_ids]

            permissions = await PermissionDocument.find(
                In(PermissionDocument.id, valid_ids), session=session
            ).to_list()

            existing_ids = {
                str(link.id if isinstance(link, PermissionDocument) else link.ref.id)
                for link in doc.permissions
            }
            
            added_count = 0
            for perm in permissions:
                if str(perm.id) not in existing_ids:
                    doc.permissions.append(perm)  # type: ignore
                    added_count += 1

            if added_count > 0:
                doc.updated_at = datetime.now(timezone.utc)
                doc.updated_by = updated_by
                doc.version += 1
                await doc.save(session=session)
                await self.log.info(tag, f"Added {added_count} permissions to feature", {"id": str(id), "count": added_count})
                
        except Exception as e:
            await self.log.error(tag, "Failed to add permissions to feature", {"error": str(e), "id": str(id)})
            raise e

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
            if isinstance(id, str) and PydanticObjectId.is_valid(id):
                id = PydanticObjectId(id)
            doc = await FeatureDocument.get(id, session=session)
            if not doc:
                raise NotFoundException(str(id), "features")

            str_ids = {str(pid) for pid in permission_ids}
            new_permissions = [
                p for p in doc.permissions 
                if str(p.id if isinstance(p, PermissionDocument) else p.ref.id) not in str_ids
            ]

            if len(new_permissions) != len(doc.permissions):
                doc.permissions = new_permissions
                doc.updated_at = datetime.now(timezone.utc)
                doc.updated_by = updated_by
                doc.version += 1
                await doc.save(session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to remove permissions from feature", {"error": str(e), "id": str(id)})
            raise e
