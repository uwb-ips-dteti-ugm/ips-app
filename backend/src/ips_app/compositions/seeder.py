import asyncio

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from ips_app.adapters.logging.generic.basic import BasicGenericLogging
from ips_app.adapters.logging.generic.json import JSONGenericLogging
from ips_app.adapters.repository.feature.beanie import BeanieFeatureRepository
from ips_app.adapters.repository.feature.beanie_model import FeatureDocument
from ips_app.adapters.repository.permission.beanie import BeaniePermissionRepository
from ips_app.adapters.repository.permission.beanie_model import PermissionDocument
from ips_app.adapters.repository.role.beanie import BeanieRoleRepository
from ips_app.adapters.repository.role.beanie_model import RoleDocument
from ips_app.adapters.repository.user.beanie import BeanieUserRepository
from ips_app.adapters.repository.user.beanie_model import UserDocument
from ips_app.config.env_var import EnvVar, load_env_var
from ips_app.domain.models.exception import ValidatorDomainException
from ips_app.domain.models.log import LogLevel
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.services.seeder.base import BaseSeeder


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
                FeatureDocument,
            ],
        )

        repo_permission = BeaniePermissionRepository(log)
        repo_role = BeanieRoleRepository(log)
        repo_feature = BeanieFeatureRepository(log)
        repo_user = BeanieUserRepository(log)

        seeder = BaseSeeder(
            admin_name=env_var.admin_name,
            admin_username=env_var.admin_username,
            admin_password=env_var.admin_password,
            repo_permission=repo_permission,
            repo_role=repo_role,
            repo_feature=repo_feature,
            repo_user=repo_user,
            log=log,
        )

        await seeder.seed_permissions()
        await seeder.seed_roles()
        await seeder.seed_features()
        await seeder.seed_accounts()
    finally:
        motor.close()


def _create_logger(env_var: EnvVar) -> GenericLogging:
    try:
        log_level = LogLevel[env_var.log_level]
    except KeyError as e:
        raise ValidatorDomainException(
            "LOG_LEVEL must be one of NONE, ERROR, WARN, INFO, or DEBUG."
        ) from e

    if env_var.log_style == "json":
        return JSONGenericLogging(log_level)
    if env_var.log_style == "basic":
        return BasicGenericLogging(log_level)

    raise ValidatorDomainException("LOG_FORMAT must be either 'basic' or 'json'.")


if __name__ == "__main__":
    asyncio.run(main())
