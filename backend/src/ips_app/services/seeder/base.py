from typing import Any, List, Optional

from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.feature import Feature
from ips_app.domain.models.permission import Permission
from ips_app.domain.models.role import Role
from ips_app.domain.models.user import User, UserPasswordAuth
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.repository.feature import FeatureRepository
from ips_app.domain.ports.driven.repository.permission import PermissionRepository
from ips_app.domain.ports.driven.repository.role import RoleRepository
from ips_app.domain.ports.driven.repository.user import UserRepository
from ips_app.domain.ports.driving.seeder.seeder import Seeder
from ips_app.config.seed_data import (
    ADMIN_ROLE_NAME,
    SEED_FEATURES,
    SEED_PERMISSIONS,
    SEED_ROLES,
    SEED_TEST_ACCOUNTS,
)
from ips_app.utils.password import hash_password


class BaseSeeder(Seeder):
    def __init__(
        self,
        admin_name: str,
        admin_username: str,
        admin_password: str,
        repo_permission: PermissionRepository,
        repo_role: RoleRepository,
        repo_feature: FeatureRepository,
        repo_user: UserRepository,
        log: GenericLogging,
    ):
        self.admin_name = admin_name
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.repo_permission = repo_permission
        self.repo_role = repo_role
        self.repo_feature = repo_feature
        self.repo_user = repo_user
        self.log = log
        self.tag_class = "BaseSeeder"

    async def seed_permissions(self) -> None:
        tag = f"{self.tag_class}.seed_permissions"
        try:
            for permission_seed in SEED_PERMISSIONS:
                permission = await self._read_permission_by_name(permission_seed["name"])
                if permission is not None:
                    continue

                await self.repo_permission.create_permission(
                    name=permission_seed["name"],
                    description=permission_seed["description"],
                )
                await self.log.info(
                    tag,
                    "Created permission",
                    {"name": permission_seed["name"]},
                )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to seed permissions",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def seed_roles(self) -> None:
        tag = f"{self.tag_class}.seed_roles"
        try:
            for role_seed in SEED_ROLES:
                role = await self._read_role_by_name(role_seed["name"])
                if role is None:
                    role = await self.repo_role.create_role(
                        name=role_seed["name"],
                        description=role_seed["description"],
                        is_default=role_seed["is_default"],
                    )
                    await self.log.info(
                        tag,
                        "Created role",
                        {"name": role_seed["name"]},
                    )

                if not role_seed["permissions"]:
                    continue

                role_detail = await self.repo_role.read_role_by_id(role.id)
                missing_ids = await self._missing_permission_ids(
                    existing_permissions=role_detail.permissions,
                    required_permission_names=role_seed["permissions"],
                )
                if not missing_ids:
                    continue

                await self.repo_role.add_permissions_to_role(
                    id=role.id,
                    permission_ids=missing_ids,
                )
                await self.log.info(
                    tag,
                    "Assigned permissions to role",
                    {"name": role_seed["name"], "count": len(missing_ids)},
                )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to seed roles",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def seed_features(self) -> None:
        tag = f"{self.tag_class}.seed_features"
        try:
            for feature_seed in SEED_FEATURES:
                feature = await self._read_feature_by_name(feature_seed["name"])
                if feature is None:
                    feature = await self.repo_feature.create_feature(
                        name=feature_seed["name"],
                        description=feature_seed["description"],
                    )
                    await self.log.info(
                        tag,
                        "Created feature",
                        {"name": feature_seed["name"]},
                    )

                if not feature_seed["permissions"]:
                    continue

                feature_detail = await self.repo_feature.read_feature_by_id(feature.id)
                missing_ids = await self._missing_permission_ids(
                    existing_permissions=feature_detail.permissions,
                    required_permission_names=feature_seed["permissions"],
                )
                if not missing_ids:
                    continue

                await self.repo_feature.add_permissions_to_feature(
                    id=feature.id,
                    permission_ids=missing_ids,
                )
                await self.log.info(
                    tag,
                    "Assigned permissions to feature",
                    {"name": feature_seed["name"], "count": len(missing_ids)},
                )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to seed features",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def seed_accounts(self) -> None:
        tag = f"{self.tag_class}.seed_accounts"
        try:
            admin_role = await self._read_role_by_name(ADMIN_ROLE_NAME)
            if admin_role is not None:
                await self._create_account_if_missing(
                    name=self.admin_name,
                    username=self.admin_username,
                    password=self.admin_password,
                    role=admin_role,
                    tag=tag,
                    label="Created admin user",
                )

            for account_seed in SEED_TEST_ACCOUNTS:
                role = await self._read_role_by_name(account_seed["role"])
                if role is None:
                    continue

                await self._create_account_if_missing(
                    name=account_seed["name"],
                    username=account_seed["username"],
                    password=account_seed["password"],
                    role=role,
                    tag=tag,
                    label="Created test user",
                )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to seed accounts",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def _read_permission_by_name(self, name: str) -> Optional[Permission]:
        try:
            return await self.repo_permission.read_permission_by_name(name)
        except NotFoundDomainException:
            return None

    async def _read_role_by_name(self, name: str) -> Optional[Role]:
        try:
            return await self.repo_role.read_role_by_name(name)
        except NotFoundDomainException:
            return None

    async def _read_feature_by_name(self, name: str) -> Optional[Feature]:
        try:
            return await self.repo_feature.read_feature_by_name(name)
        except NotFoundDomainException:
            return None

    async def _read_user_by_username(self, username: str) -> Optional[User]:
        try:
            return await self.repo_user.read_user_by_username(username)
        except NotFoundDomainException:
            return None

    async def _missing_permission_ids(
        self,
        existing_permissions: List[Permission],
        required_permission_names: List[str],
    ) -> List[Any]:
        existing_permission_names = {
            permission.name
            for permission in existing_permissions
        }
        missing_ids: List[Any] = []
        for permission_name in required_permission_names:
            if permission_name in existing_permission_names:
                continue

            permission = await self._read_permission_by_name(permission_name)
            if permission is not None:
                missing_ids.append(permission.id)

        return missing_ids

    async def _create_account_if_missing(
        self,
        name: str,
        username: str,
        password: str,
        role: Role,
        tag: str,
        label: str,
    ) -> None:
        existing = await self._read_user_by_username(username)
        if existing is not None:
            return

        await self.repo_user.create_user(
            role_id=role.id,
            name=name,
            auths=[
                UserPasswordAuth(
                    username=username,
                    password_hash=hash_password(password),
                )
            ],
        )
        await self.log.info(tag, label, {"username": username})
