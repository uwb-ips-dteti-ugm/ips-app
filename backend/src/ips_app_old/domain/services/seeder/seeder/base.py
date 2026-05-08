from ips_app_old.ports.driving.seeder.seeder import SeederPort
from ips_app_old.ports.driven.repository.permission import PermissionRepositoryPort
from ips_app_old.ports.driven.repository.role import RoleRepositoryPort
from ips_app_old.ports.driven.repository.feature import FeatureRepositoryPort
from ips_app_old.ports.driven.repository.user import UserRepositoryPort
from ips_app_old.ports.driven.repository.auth import AuthRepositoryPort
from ips_app_old.ports.driven.logging.generic import GenericLoggingPort
from ips_app_old.utils.password import hash_password
from ips_app_old.domain.services.seeder.seeder.seeds import (
    SEED_PERMISSIONS,
    SEED_ROLES,
    SEED_FEATURES,
    SEED_TEST_ACCOUNTS,
    ADMIN_ROLE_NAME,
)


class SeederService(SeederPort):
    def __init__(
        self,
        admin_name: str,
        admin_username: str,
        admin_password: str,
        repo_perm: PermissionRepositoryPort,
        repo_role: RoleRepositoryPort,
        repo_feat: FeatureRepositoryPort,
        repo_user: UserRepositoryPort,
        repo_auth: AuthRepositoryPort,
        log: GenericLoggingPort,
    ):
        self.admin_name = admin_name
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.repo_perm = repo_perm
        self.repo_role = repo_role
        self.repo_feat = repo_feat
        self.repo_user = repo_user
        self.repo_auth = repo_auth
        self.log = log
        self.tag_class = "SeederService"

    async def seed_permissions(self) -> None:
        tag = f"{self.tag_class}.seed_permissions"
        for perm in SEED_PERMISSIONS:
            existing = await self.repo_perm.read_permission_by_name(perm["name"])
            if not existing:
                await self.repo_perm.create_permission(name=perm["name"], description=perm["description"])
                await self.log.info(tag, "Created permission", {"name": perm["name"]})

    async def seed_roles(self) -> None:
        tag = f"{self.tag_class}.seed_roles"
        for role_data in SEED_ROLES:
            role = await self.repo_role.read_role_by_name(role_data["name"])
            if not role:
                role = await self.repo_role.create_role(
                    name=role_data["name"],
                    description=role_data["description"],
                    is_default=role_data["is_default"],
                )
                await self.log.info(tag, "Created role", {"name": role_data["name"]})

            if not role_data["permissions"]:
                continue

            role_detail = await self.repo_role.read_role_by_id(role.id)
            if role_detail is None:
                continue

            existing_perm_names = {p.name for p in role_detail.permissions}
            missing_ids = []
            for perm_name in role_data["permissions"]:
                if perm_name not in existing_perm_names:
                    perm = await self.repo_perm.read_permission_by_name(perm_name)
                    if perm:
                        missing_ids.append(perm.id)

            if missing_ids:
                await self.repo_role.add_permissions_to_role(id=role.id, permission_ids=missing_ids)
                await self.log.info(tag, "Assigned permissions to role", {"name": role_data["name"]})

    async def seed_features(self) -> None:
        tag = f"{self.tag_class}.seed_features"
        for feat_data in SEED_FEATURES:
            name = feat_data["name"]
            feat = await self.repo_feat.read_feature_by_name(name)

            if not feat:
                feat = await self.repo_feat.create_feature(name=name, description=feat_data["description"])
                await self.log.info(tag, "Created feature", {"name": name})

            if not feat_data["permissions"]:
                continue

            feat_detail = await self.repo_feat.read_feature_by_id(feat.id)
            if feat_detail is None:
                continue

            existing_perm_names = {p.name for p in feat_detail.permissions}
            missing_ids = []
            for perm_name in feat_data["permissions"]:
                if perm_name not in existing_perm_names:
                    perm = await self.repo_perm.read_permission_by_name(perm_name)
                    if perm:
                        missing_ids.append(perm.id)

            if missing_ids:
                await self.repo_feat.add_permissions_to_feature(id=feat.id, permission_ids=missing_ids)
                await self.log.info(tag, "Assigned permissions to feature", {"name": name})

    async def seed_accounts(self) -> None:
        tag = f"{self.tag_class}.seed_accounts"

        admin_role = await self.repo_role.read_role_by_name(ADMIN_ROLE_NAME)
        if admin_role:
            existing = await self.repo_auth.read_auth_by_sign_in_identifier(self.admin_username)
            if not existing:
                user = await self.repo_user.create_user(role_id=admin_role.id, name=self.admin_name)
                await self.repo_auth.create_auth(
                    user_id=user.id,
                    username=self.admin_username,
                    password_hash=hash_password(self.admin_password),
                )
                await self.log.info(tag, "Created admin user", {"username": self.admin_username})

        for account in SEED_TEST_ACCOUNTS:
            role = await self.repo_role.read_role_by_name(account["role"])
            if not role:
                continue

            existing = await self.repo_auth.read_auth_by_sign_in_identifier(account["username"])
            if not existing:
                user = await self.repo_user.create_user(role_id=role.id, name=account["name"])
                await self.repo_auth.create_auth(
                    user_id=user.id,
                    username=account["username"],
                    password_hash=hash_password(account["password"]),
                )
                await self.log.info(tag, "Created test user", {"username": account["username"]})
