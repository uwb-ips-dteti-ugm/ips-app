import json
from typing import Any, List, Optional, Tuple

from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.feature import Feature
from ips_app.domain.models.user import User, UserState, UserStatus
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.repository.feature import FeatureRepository
from ips_app.domain.ports.driven.repository.role import RoleRepository
from ips_app.domain.ports.driven.repository.user import UserRepository
from ips_app.domain.ports.driving.http.user import UserHTTP


class BaseUserHTTP(UserHTTP):
    def __init__(
        self,
        repo: UserRepository,
        repo_feature: FeatureRepository,
        repo_role: RoleRepository,
        log: GenericLogging,
    ):
        self.repo = repo
        self.repo_feature = repo_feature
        self.repo_role = repo_role
        self.log = log
        self.tag_class = self.__class__.__name__

    async def get_user(self, user_id: Any) -> User:
        tag = f"{self.tag_class}.get_user"
        try:
            return await self.repo.read_user_by_id(user_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get user",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_users(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        role_id: Optional[Any] = None,
    ) -> Tuple[List[User], int]:
        tag = f"{self.tag_class}.get_users"
        try:
            return await self.repo.read_users_by_pagination(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
                role_id=role_id,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get users",
                {"error": str(e), "page": page, "limit": limit},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_user_info(
        self,
        user_id: Any,
        name: Optional[str] = None,
        bio: Optional[str] = None,
    ) -> User:
        tag = f"{self.tag_class}.set_user_info"
        try:
            await self.repo.update_user_info_by_id(user_id, name, bio)
            user = await self.get_user(user_id)
            await self.log.info(
                tag,
                "Successfully updated user info",
                {"id": str(user_id)},
            )
            return user
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set user info",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_user_preferences(self, user_id: Any, preferences: bytes) -> User:
        tag = f"{self.tag_class}.set_user_preferences"
        try:
            preferences_dict = json.loads(preferences)
            await self.repo.update_user_preferences_by_id(user_id, preferences_dict)
            user = await self.get_user(user_id)
            await self.log.info(
                tag,
                "Successfully updated user preferences",
                {"id": str(user_id)},
            )
            return user
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set user preferences",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_user_role(self, user_id: Any, role_id: Any) -> User:
        tag = f"{self.tag_class}.set_user_role"
        try:
            await self.repo.update_user_role_by_id(user_id, role_id)
            user = await self.get_user(user_id)
            await self.log.info(
                tag,
                "Successfully updated user role",
                {"id": str(user_id), "role_id": str(role_id)},
            )
            return user
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set user role",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_user_state(self, user_id: Any, state: UserState) -> User:
        tag = f"{self.tag_class}.set_user_state"
        try:
            await self.repo.update_user_state_by_id(user_id, state)
            user = await self.get_user(user_id)
            await self.log.info(
                tag,
                "Successfully updated user state",
                {"id": str(user_id), "state": str(state)},
            )
            return user
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set user state",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_user_status(self, user_id: Any, status: UserStatus) -> User:
        tag = f"{self.tag_class}.set_user_status"
        try:
            await self.repo.update_user_status_by_id(user_id, status)
            user = await self.get_user(user_id)
            await self.log.info(
                tag,
                "Successfully updated user status",
                {"id": str(user_id), "status": str(status)},
            )
            return user
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set user status",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_user_last_activity(self, user_id: Any) -> None:
        tag = f"{self.tag_class}.set_user_last_activity"
        try:
            user = await self.repo.read_user_by_id(user_id)
            await self.repo.update_user_last_activity_at_by_id(user_id)
            await self._set_user_online_unless_dnd(user)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set user last activity",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_user(self, user_id: Any) -> str:
        tag = f"{self.tag_class}.remove_user"
        try:
            await self.repo.delete_user_by_id(user_id)
            await self.log.info(
                tag,
                "Successfully removed user",
                {"id": str(user_id)},
            )
            return "User removed successfully"
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove user",
                {"error": str(e), "id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_accessible_features(self, user_id: Any) -> List[Feature]:
        tag = f"{self.tag_class}.get_accessible_features"
        try:
            role_permission_ids = await self._get_user_role_permission_ids(user_id)
            if not role_permission_ids:
                await self.log.info(
                    tag,
                    "Fetched accessible features",
                    {"user_id": str(user_id), "count": 0},
                )
                return []

            accessible_features: List[Feature] = []
            page = 0
            limit = 100

            while True:
                features, total = await self.repo_feature.read_features_by_pagination(
                    page=page,
                    limit=limit,
                )
                accessible_features.extend(
                    feature
                    for feature in features
                    if self._can_access_feature(feature, role_permission_ids)
                )

                if len(features) < limit or (page + 1) * limit >= total:
                    break
                page += 1

            await self.log.info(
                tag,
                "Fetched accessible features",
                {"user_id": str(user_id), "count": len(accessible_features)},
            )
            return accessible_features
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get accessible features",
                {"error": str(e), "user_id": str(user_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def can_access_feature_by_name(self, user_id: Any, feature_name: str) -> bool:
        tag = f"{self.tag_class}.can_access_feature_by_name"
        try:
            role_permission_ids = await self._get_user_role_permission_ids(user_id)
            feature = await self.repo_feature.read_feature_by_name(feature_name)
            result = self._can_access_feature(feature, role_permission_ids)

            await self.log.info(
                tag,
                "Checked feature access by name",
                {
                    "user_id": str(user_id),
                    "feature_name": feature_name,
                    "result": result,
                },
            )
            return result
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to check feature access by name",
                {
                    "error": str(e),
                    "user_id": str(user_id),
                    "feature_name": feature_name,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def _get_user_role_permission_ids(self, user_id: Any) -> set[str]:
        user = await self.repo.read_user_by_id(user_id)
        if user.role is None or user.role.id is None:
            return set()

        role = await self.repo_role.read_role_by_id(user.role.id)
        return {
            str(permission.id)
            for permission in role.permissions
            if permission.id is not None
        }

    def _can_access_feature(
        self,
        feature: Feature,
        role_permission_ids: set[str],
    ) -> bool:
        feature_permission_ids = {
            str(permission.id)
            for permission in feature.permissions
            if permission.id is not None
        }
        return bool(role_permission_ids & feature_permission_ids)

    async def _set_user_online_unless_dnd(self, user: User) -> None:
        if user.state == UserState.DND:
            return
        await self.repo.update_user_state_by_id(user.id, UserState.ONLINE)
