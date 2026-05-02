import json
from typing import Optional, List, Tuple, Any
from ips_app.domain.models.feature import Feature
from ips_app.domain.models.permission import Permission
from ips_app.ports.driving.http.feature import FeatureHTTPPort
from ips_app.ports.driven.repository.feature import FeatureRepositoryPort
from ips_app.ports.driven.repository.user import UserRepositoryPort
from ips_app.ports.driven.repository.role import RoleRepositoryPort
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.domain.models.exception import NotFoundException


class FeatureHTTPService(FeatureHTTPPort):
    def __init__(
        self,
        repo: FeatureRepositoryPort,
        repo_user: UserRepositoryPort,
        repo_role: RoleRepositoryPort,
        log: GenericLoggingPort,
    ):
        self.repo = repo
        self.repo_user = repo_user
        self.repo_role = repo_role
        self.log = log
        self.tag_class = "FeatureHTTPService"

    async def add_feature(self, name: str, description: str) -> Feature:
        tag = f"{self.tag_class}.add_feature"
        try:
            feature = await self.repo.create_feature(name=name, description=description)
            await self.log.info(tag, "Successfully added feature", {"id": str(feature.id), "name": name})
            return feature
        except Exception as e:
            await self.log.error(tag, "Failed to add feature", {"error": str(e), "name": name})
            raise e

    async def get_feature(self, feature_id: Any) -> Feature:
        tag = f"{self.tag_class}.get_feature"
        try:
            feature = await self.repo.read_feature_by_id(feature_id)
            if not feature:
                raise NotFoundException(str(feature_id), "features")
            return feature
        except Exception as e:
            await self.log.error(tag, "Failed to get feature", {"error": str(e), "id": str(feature_id)})
            raise e

    async def get_features(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Feature], int]:
        tag = f"{self.tag_class}.get_features"
        try:
            return await self.repo.read_features_by_pagination(page, limit, cursor_id, search)
        except Exception as e:
            await self.log.error(tag, "Failed to get features", {"error": str(e), "page": page, "limit": limit})
            raise e

    async def set_feature(
        self,
        feature_id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Feature:
        tag = f"{self.tag_class}.set_feature"
        try:
            await self.repo.update_feature_by_id(feature_id, name, description)
            feature = await self.get_feature(feature_id)
            await self.log.info(tag, "Successfully updated feature", {"id": str(feature_id)})
            return feature
        except Exception as e:
            await self.log.error(tag, "Failed to set feature", {"error": str(e), "id": str(feature_id)})
            raise e

    async def set_feature_preferences(self, feature_id: Any, preferences: bytes) -> Feature:
        tag = f"{self.tag_class}.set_feature_preferences"
        try:
            prefs_dict = json.loads(preferences)
            await self.repo.update_feature_preferences_by_id(feature_id, prefs_dict)
            feature = await self.get_feature(feature_id)
            await self.log.info(tag, "Successfully updated feature preferences", {"id": str(feature_id)})
            return feature
        except Exception as e:
            await self.log.error(tag, "Failed to set feature preferences", {"error": str(e), "id": str(feature_id)})
            raise e

    async def remove_feature(self, feature_id: Any) -> str:
        tag = f"{self.tag_class}.remove_feature"
        try:
            await self.repo.delete_feature_by_id(feature_id)
            await self.log.info(tag, "Successfully removed feature", {"id": str(feature_id)})
            return "Feature removed successfully"
        except Exception as e:
            await self.log.error(tag, "Failed to remove feature", {"error": str(e), "id": str(feature_id)})
            raise e

    async def add_permissions_to_feature(self, feature_id: Any, permission_ids: List[Any]) -> Feature:
        tag = f"{self.tag_class}.add_permissions_to_feature"
        try:
            await self.repo.add_permissions_to_feature(feature_id, permission_ids)
            feature = await self.get_feature(feature_id)
            await self.log.info(tag, "Successfully added permissions to feature", {"id": str(feature_id), "permission_ids": [str(pid) for pid in permission_ids]})
            return feature
        except Exception as e:
            await self.log.error(tag, "Failed to add permissions to feature", {"error": str(e), "id": str(feature_id)})
            raise e

    async def remove_permissions_from_feature(self, feature_id: Any, permission_ids: List[Any]) -> Feature:
        tag = f"{self.tag_class}.remove_permissions_from_feature"
        try:
            await self.repo.remove_permissions_from_feature(feature_id, permission_ids)
            feature = await self.get_feature(feature_id)
            await self.log.info(tag, "Successfully removed permissions from feature", {"id": str(feature_id), "permission_ids": [str(pid) for pid in permission_ids]})
            return feature
        except Exception as e:
            await self.log.error(tag, "Failed to remove permissions from feature", {"error": str(e), "id": str(feature_id)})
            raise e

    async def get_feature_permissions(self, feature_id: Any) -> List[Permission]:
        tag = f"{self.tag_class}.get_feature_permissions"
        try:
            feature = await self.get_feature(feature_id)
            return feature.permissions
        except Exception as e:
            await self.log.error(tag, "Failed to get feature permissions", {"error": str(e), "id": str(feature_id)})
            raise e

    async def _get_user_role_permission_ids(self, user_id: Any) -> set:
        user = await self.repo_user.read_user_by_id(user_id)
        if not user:
            raise NotFoundException(str(user_id), "users")

        role = await self.repo_role.read_role_by_id(user.role.id)
        if not role:
            raise NotFoundException(str(user.role.id), "roles")

        return {str(p.id) for p in role.permissions}

    async def get_accessible_features(self, user_id: Any) -> List[Feature]:
        tag = f"{self.tag_class}.get_accessible_features"
        try:
            role_permission_ids = await self._get_user_role_permission_ids(user_id)

            accessible: List[Feature] = []
            page = 0
            limit = 100
            while True:
                features, _ = await self.repo.read_features_by_pagination(page, limit)
                for feature in features:
                    feature_permission_ids = {str(p.id) for p in feature.permissions}
                    if role_permission_ids & feature_permission_ids:
                        accessible.append(feature)
                if len(features) < limit:
                    break
                page += 1

            await self.log.info(tag, "Fetched accessible features", {"user_id": str(user_id), "count": len(accessible)})
            return accessible
        except Exception as e:
            await self.log.error(tag, "Failed to get accessible features", {"error": str(e), "user_id": str(user_id)})
            raise e

    async def can_access_feature(self, user_id: Any, feature_id: Any) -> bool:
        tag = f"{self.tag_class}.can_access_feature"
        try:
            role_permission_ids = await self._get_user_role_permission_ids(user_id)

            feature = await self.repo.read_feature_by_id(feature_id)
            if not feature:
                raise NotFoundException(str(feature_id), "features")

            feature_permission_ids = {str(p.id) for p in feature.permissions}
            result = bool(role_permission_ids & feature_permission_ids)

            await self.log.info(tag, "Checked feature access", {"user_id": str(user_id), "feature_id": str(feature_id), "result": result})
            return result
        except Exception as e:
            await self.log.error(tag, "Failed to check feature access", {"error": str(e), "user_id": str(user_id), "feature_id": str(feature_id)})
            raise e

    async def can_access_feature_by_name(self, user_id: Any, feature_name: str) -> bool:
        tag = f"{self.tag_class}.can_access_feature_by_name"
        try:
            role_permission_ids = await self._get_user_role_permission_ids(user_id)

            feature = await self.repo.read_feature_by_name(feature_name)
            if not feature:
                raise NotFoundException(feature_name, "features")

            feature_permission_ids = {str(p.id) for p in feature.permissions}
            result = bool(role_permission_ids & feature_permission_ids)

            await self.log.info(tag, "Checked feature access by name", {"user_id": str(user_id), "feature_name": feature_name, "result": result})
            return result
        except Exception as e:
            await self.log.error(tag, "Failed to check feature access by name", {"error": str(e), "user_id": str(user_id), "feature_name": feature_name})
            raise e
