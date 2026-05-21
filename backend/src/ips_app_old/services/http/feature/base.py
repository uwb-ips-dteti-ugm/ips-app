import json
from typing import Any, List, Optional, Tuple

from ips_app_old.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app_old.domain.models.feature import Feature
from ips_app_old.domain.models.permission import Permission
from ips_app_old.domain.ports.driven.logging.generic import GenericLogging
from ips_app_old.domain.ports.driven.repository.feature import FeatureRepository
from ips_app_old.domain.ports.driving.http.feature import FeatureHTTP


class BaseFeatureHTTP(FeatureHTTP):
    def __init__(
        self,
        repo: FeatureRepository,
        log: GenericLogging,
    ):
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def add_feature(self, name: str, description: str) -> Feature:
        tag = f"{self.tag_class}.add_feature"
        try:
            feature = await self.repo.create_feature(name=name, description=description)
            await self.log.info(
                tag,
                "Successfully added feature",
                {"id": str(feature.id), "name": name},
            )
            return feature
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add feature",
                {"error": str(e), "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_feature(self, feature_id: Any) -> Feature:
        tag = f"{self.tag_class}.get_feature"
        try:
            return await self.repo.read_feature_by_id(feature_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get feature",
                {"error": str(e), "id": str(feature_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_features(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Feature], int]:
        tag = f"{self.tag_class}.get_features"
        try:
            return await self.repo.read_features_by_pagination(
                page,
                limit,
                cursor_id,
                search,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get features",
                {"error": str(e), "page": page, "limit": limit},
            )
            raise UnexpectedDomainException(str(e)) from e

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
            await self.log.info(
                tag,
                "Successfully updated feature",
                {"id": str(feature_id)},
            )
            return feature
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set feature",
                {"error": str(e), "id": str(feature_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_feature_preferences(self, feature_id: Any, preferences: bytes) -> Feature:
        tag = f"{self.tag_class}.set_feature_preferences"
        try:
            preferences_dict = json.loads(preferences)
            await self.repo.update_feature_preferences_by_id(feature_id, preferences_dict)
            feature = await self.get_feature(feature_id)
            await self.log.info(
                tag,
                "Successfully updated feature preferences",
                {"id": str(feature_id)},
            )
            return feature
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set feature preferences",
                {"error": str(e), "id": str(feature_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_feature(self, feature_id: Any) -> str:
        tag = f"{self.tag_class}.remove_feature"
        try:
            await self.repo.delete_feature_by_id(feature_id)
            await self.log.info(
                tag,
                "Successfully removed feature",
                {"id": str(feature_id)},
            )
            return "Feature removed successfully"
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove feature",
                {"error": str(e), "id": str(feature_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def add_permissions_to_feature(
        self,
        feature_id: Any,
        permission_ids: List[Any],
    ) -> Feature:
        tag = f"{self.tag_class}.add_permissions_to_feature"
        try:
            await self.repo.add_permissions_to_feature(feature_id, permission_ids)
            feature = await self.get_feature(feature_id)
            await self.log.info(
                tag,
                "Successfully added permissions to feature",
                {
                    "id": str(feature_id),
                    "permission_ids": [str(permission_id) for permission_id in permission_ids],
                },
            )
            return feature
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add permissions to feature",
                {"error": str(e), "id": str(feature_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_permissions_from_feature(
        self,
        feature_id: Any,
        permission_ids: List[Any],
    ) -> Feature:
        tag = f"{self.tag_class}.remove_permissions_from_feature"
        try:
            await self.repo.remove_permissions_from_feature(feature_id, permission_ids)
            feature = await self.get_feature(feature_id)
            await self.log.info(
                tag,
                "Successfully removed permissions from feature",
                {
                    "id": str(feature_id),
                    "permission_ids": [str(permission_id) for permission_id in permission_ids],
                },
            )
            return feature
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove permissions from feature",
                {"error": str(e), "id": str(feature_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_feature_permissions(self, feature_id: Any) -> List[Permission]:
        tag = f"{self.tag_class}.get_feature_permissions"
        try:
            feature = await self.get_feature(feature_id)
            return feature.permissions
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get feature permissions",
                {"error": str(e), "id": str(feature_id)},
            )
            raise UnexpectedDomainException(str(e)) from e
