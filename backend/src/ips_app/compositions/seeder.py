import asyncio

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from ips_app.adapters.logging.leveled.basic import BasicLeveledLogging
from ips_app.adapters.logging.leveled.json import JSONLeveledLogging
from ips_app.adapters.repository.permission.beanie import BeaniePermissionRepository
from ips_app.adapters.repository.permission.beanie_model import PermissionDocument
from ips_app.adapters.repository.role.beanie import BeanieRoleRepository
from ips_app.adapters.repository.role.beanie_model import RoleDocument
from ips_app.adapters.repository.user.beanie import BeanieUserRepository
from ips_app.adapters.repository.user.beanie_model import UserDocument
from ips_app.config.env_var import EnvVar, load_env_var
from ips_app.controllers.seeder.permission import PermissionSeederController
from ips_app.controllers.seeder.role import RoleSeederController
from ips_app.controllers.seeder.user import UserSeederController
from ips_app.domain.models.exception import ValidatorDomainException
from ips_app.domain.models.log import LogLevel
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.services.seeder.permission.base import BasePermissionSeeder
from ips_app.services.seeder.role.base import BaseRoleSeeder
from ips_app.services.seeder.user.base import BaseUserSeeder


async def main() -> None:
    env_var = load_env_var()
    log = _create_logger(env_var)

    motor = AsyncIOMotorClient(env_var.mongo_uri)
    try:
        await init_beanie(
            database=motor[env_var.mongo_db],  # type: ignore[arg-type]
            document_models=[
                PermissionDocument,
                RoleDocument,
                UserDocument,
            ],
        )

        repo_permission = BeaniePermissionRepository(log)
        repo_role = BeanieRoleRepository(log)
        repo_user = BeanieUserRepository(log)

        permission_controller = PermissionSeederController(
            BasePermissionSeeder(repo_permission, log),
        )
        role_controller = RoleSeederController(
            BaseRoleSeeder(repo_role, repo_permission, log),
        )
        user_controller = UserSeederController(
            BaseUserSeeder(repo_user, repo_role, log),
            admin_name=env_var.seeder_admin_name,
            admin_username=env_var.seeder_admin_username,
            admin_password=env_var.seeder_admin_password,
            user_name=env_var.seeder_user_name,
            user_username=env_var.seeder_user_username,
            user_password=env_var.seeder_user_password,
        )

        await permission_controller.seed()
        await role_controller.seed()
        await user_controller.seed()
    finally:
        motor.close()


def _create_logger(env_var: EnvVar) -> LeveledLogging:
    try:
        log_level = LogLevel[env_var.log_level]
    except KeyError as e:
        raise ValidatorDomainException(
            "LOG_LEVEL must be one of NONE, ERROR, WARN, INFO, or DEBUG."
        ) from e

    if env_var.log_style == "json":
        return JSONLeveledLogging(log_level)
    if env_var.log_style == "basic":
        return BasicLeveledLogging(log_level)

    raise ValidatorDomainException("LOG_FORMAT must be either 'basic' or 'json'.")


if __name__ == "__main__":
    asyncio.run(main())
