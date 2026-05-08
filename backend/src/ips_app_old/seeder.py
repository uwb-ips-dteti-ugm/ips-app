import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from ips_app_old.config.env_var import load_env_var
from ips_app_old.domain.models.logging import LogLevel

from ips_app_old.adapters.driven.logging.generic.basic import BasicGenericLogging
from ips_app_old.adapters.driven.logging.generic.json import JSONGenericLogging

from ips_app_old.adapters.driven.repository.auth.beanie import BeanieAuthRepository
from ips_app_old.adapters.driven.repository.user.beanie import BeanieUserRepository
from ips_app_old.adapters.driven.repository.role.beanie import BeanieRoleRepository
from ips_app_old.adapters.driven.repository.permission.beanie import BeaniePermissionRepository
from ips_app_old.adapters.driven.repository.feature.beanie import BeanieFeatureRepository

from ips_app_old.adapters.driven.repository.permission.beanie_model import PermissionDocument
from ips_app_old.adapters.driven.repository.role.beanie_model import RoleDocument
from ips_app_old.adapters.driven.repository.user.beanie_model import UserDocument
from ips_app_old.adapters.driven.repository.auth.beanie_model import AuthDocument
from ips_app_old.adapters.driven.repository.feature.beanie_model import FeatureDocument

from ips_app_old.domain.services.seeder.seeder.base import SeederService


async def main() -> None:
    env_var = load_env_var()

    log_level = LogLevel[env_var.log_level]
    log = JSONGenericLogging(log_level) if env_var.log_style == "json" else BasicGenericLogging(log_level)

    motor = AsyncIOMotorClient(env_var.mongo_uri)
    try:
        await init_beanie(
            database=motor[env_var.mongo_db],  # type: ignore[arg-type]
            document_models=[
                PermissionDocument,
                RoleDocument,
                UserDocument,
                AuthDocument,
                FeatureDocument,
            ],
        )

        seeder = SeederService(
            admin_name=env_var.admin_name,
            admin_username=env_var.admin_username,
            admin_password=env_var.admin_password,
            repo_perm=BeaniePermissionRepository(log),
            repo_role=BeanieRoleRepository(log),
            repo_feat=BeanieFeatureRepository(log),
            repo_user=BeanieUserRepository(log),
            repo_auth=BeanieAuthRepository(log),
            log=log,
        )

        await seeder.seed_permissions()
        await seeder.seed_roles()
        await seeder.seed_features()
        await seeder.seed_accounts()
    finally:
        motor.close()


if __name__ == "__main__":
    asyncio.run(main())
