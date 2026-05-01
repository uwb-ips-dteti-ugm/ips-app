from typing import Optional, List, Tuple, Any, Dict
from ips_app.domain.models.feature import Feature
from ips_app.domain.models.permission import Permission
from ips_app.ports.driven.repository.feature import FeatureRepositoryPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.domain.models.exception import NotFoundException, DuplicateException
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from beanie.operators import In

class BeanieFeatureRepository(FeatureRepositoryPort):
    def __init__(self, log: GenericLoggingPort):
        self.log = log
        self.tag_class = "BeanieFeatureRepository"

    async def create_feature(
        self, 
        name: str, 
        description: str, 
        created_by: Optional[int] = None
    ) -> Feature:
        tag = f"{self.tag_class}.create_feature"
        try:
            feature = Feature(name=name, description=description, created_by=created_by)
            await feature.insert()
            return feature
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate feature name", {"error": str(e), "name": name})
            raise DuplicateException("name", "features")
        except Exception as e:
            await self.log.error(tag, "Failed to create feature", {"error": str(e)})
            raise e

    async def read_feature_by_id(self, id: Any) -> Optional[Feature]:
        tag = f"{self.tag_class}.read_feature_by_id"
        try:
            return await Feature.get(id, fetch_links=True)
        except Exception as e:
            await self.log.error(tag, "Failed to read feature by id", {"error": str(e), "id": str(id)})
            raise e

    async def read_features_by_pagination(
        self, 
        page: int, 
        limit: int, 
        cursor_id: Optional[Any] = None, 
        search: Optional[str] = None
    ) -> Tuple[List[Feature], int]:
        tag = f"{self.tag_class}.read_features_by_pagination"
        try:
            query = Feature.find_all()
            if search:
                query = Feature.find({"name": {"$regex": search, "$options": "i"}})
            
            if cursor_id:
                query = query.find({"_id": {"$gt": cursor_id}})
            
            total = await query.count()
            items = await query.skip(page * limit).limit(limit).to_list()
            return items, total
        except Exception as e:
            await self.log.error(tag, "Failed to read features by pagination", {"error": str(e)})
            raise e

    async def update_feature_by_id(
        self, 
        id: Any, 
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        updated_by: Optional[int] = None
    ) -> None:
        tag = f"{self.tag_class}.update_feature_by_id"
        try:
            feature = await Feature.get(id)
            if not feature:
                raise NotFoundException(str(id), "features")
            
            update_data = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": feature.version + 1
            }
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            
            await feature.set(update_data)
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
        updated_by: Optional[int] = None
    ) -> None:
        tag = f"{self.tag_class}.update_feature_preferences_by_id"
        try:
            feature = await Feature.get(id)
            if not feature:
                raise NotFoundException(str(id), "features")
            
            await feature.set({
                "preferences": preferences,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": feature.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to update feature preferences", {"error": str(e), "id": str(id)})
            raise e

    async def delete_feature_by_id(self, id: Any) -> None:
        tag = f"{self.tag_class}.delete_feature_by_id"
        try:
            feature = await Feature.get(id)
            if not feature:
                raise NotFoundException(str(id), "features")
            await feature.delete()
        except Exception as e:
            await self.log.error(tag, "Failed to delete feature", {"error": str(e), "id": str(id)})
            raise e

    async def add_permissions_to_feature(self, id: Any, permission_ids: List[Any], updated_by: Optional[int] = None) -> None:
        tag = f"{self.tag_class}.add_permissions_to_feature"
        try:
            feature = await Feature.get(id)
            if not feature:
                raise NotFoundException(str(id), "features")
            
            permissions = await Permission.find(In(Permission.id, permission_ids)).to_list()
            
            # Using a set of ID strings to avoid duplicates
            existing_ids = {str(link.ref.id) for link in feature.permissions}
            
            for perm in permissions:
                if str(perm.id) not in existing_ids:
                    feature.permissions.append(perm) # type: ignore
                
            await feature.set({
                "permissions": feature.permissions,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": feature.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to add permissions to feature", {"error": str(e), "id": str(id)})
            raise e

    async def remove_permissions_from_feature(self, id: Any, permission_ids: List[Any], updated_by: Optional[int] = None) -> None:
        tag = f"{self.tag_class}.remove_permissions_from_feature"
        try:
            feature = await Feature.get(id)
            if not feature:
                raise NotFoundException(str(id), "features")
            
            str_ids = {str(pid) for pid in permission_ids}
            feature.permissions = [p for p in feature.permissions if str(p.ref.id) not in str_ids]
            
            await feature.set({
                "permissions": feature.permissions,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": feature.version + 1
            })
        except Exception as e:
            await self.log.error(tag, "Failed to remove permissions from feature", {"error": str(e), "id": str(id)})
            raise e
