from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from ips_app.application.permission.permission import BasePermissionUsecase
from ips_app.application.role.role import BaseRoleUsecase
from ips_app.application.user.user import BaseUserUsecase
from ips_app.composition._shared.logger import create_logger
from ips_app.composition.seeder.permission import seed_permissions
from ips_app.composition.seeder.role import seed_roles
from ips_app.composition.seeder.user import seed_users
from ips_app.config import env
from ips_app.config.seed_data import build_seed_users
from ips_app.infrastructure.repository.permission.beanie import BeaniePermissionRepository
from ips_app.infrastructure.repository.permission.beanie_model import PermissionDocument
from ips_app.infrastructure.repository.role.beanie import BeanieRoleRepository
from ips_app.infrastructure.repository.role.beanie_model import RoleDocument
from ips_app.infrastructure.repository.user.beanie import BeanieUserRepository
from ips_app.infrastructure.repository.user.beanie_model import UserDocument
from ips_app.infrastructure.utility.password.bcrypt import BcryptPasswordHasher


async def main() -> None:
    env.load_env()
    log = create_logger()

    motor = AsyncIOMotorClient(env.APP_MONGO_URI)
    try:
        await init_beanie(
            database=motor[env.APP_MONGO_DB],
            document_models=[PermissionDocument, RoleDocument, UserDocument],
        )

        permission_usecase = BasePermissionUsecase(BeaniePermissionRepository(), log)
        role_usecase = BaseRoleUsecase(BeanieRoleRepository(), log)
        user_usecase = BaseUserUsecase(BeanieUserRepository(), BcryptPasswordHasher(), log)

        await seed_permissions(permission_usecase)
        await seed_roles(permission_usecase, role_usecase)
        await seed_users(
            role_usecase,
            user_usecase,
            build_seed_users(
                admin_name=env.APP_SEEDER_ADMIN_NAME,
                admin_username=env.APP_SEEDER_ADMIN_USERNAME,
                admin_password=env.APP_SEEDER_ADMIN_PASSWORD,
                user_name=env.APP_SEEDER_USER_NAME,
                user_username=env.APP_SEEDER_USER_USERNAME,
                user_password=env.APP_SEEDER_USER_PASSWORD,
            ),
        )
    finally:
        motor.close()
