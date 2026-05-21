from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.user import User, UserPasswordAuth
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.role import RoleRepository
from ips_app.domain.ports.driven.repository.user import UserRepository
from ips_app.domain.ports.driving.seeder.user import UserSeeder
from ips_app.utils.password import hash_password


class BaseUserSeeder(UserSeeder):
    def __init__(
        self,
        repo_user: UserRepository,
        repo_role: RoleRepository,
        log: LeveledLogging,
    ):
        self.repo_user = repo_user
        self.repo_role = repo_role
        self.log = log
        self.tag_class = self.__class__.__name__

    async def user_exists(self, username: str) -> bool:
        tag = f"{self.tag_class}.user_exists"
        try:
            await self.repo_user.read_user_by_password_username(username)
            return True
        except NotFoundDomainException:
            return False
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to check user existence",
                {"error": str(e), "username": username},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def add_user(
        self,
        name: str,
        username: str,
        password: str,
        role_name: str,
    ) -> User:
        tag = f"{self.tag_class}.add_user"
        try:
            role = await self.repo_role.read_role_by_name(role_name)
            user = await self.repo_user.create_user(
                role_id=role.id,
                name=name,
            )
            try:
                await self.repo_user.add_user_auth_by_id(
                    id=user.id,
                    auth=UserPasswordAuth(
                        username=username,
                        password_hash=hash_password(password),
                    ),
                )
            except DomainException:
                try:
                    await self.repo_user.delete_user_by_id(user.id)
                except Exception as rollback_error:
                    await self.log.error(
                        tag,
                        "Failed to roll back seeded user",
                        {"error": str(rollback_error), "id": str(user.id)},
                    )
                raise

            user = await self.repo_user.read_user_by_id(user.id)
            await self.log.info(
                tag,
                "Added seeded user",
                {
                    "id": str(user.id),
                    "username": username,
                    "role_name": role_name,
                },
            )
            return user
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add seeded user",
                {"error": str(e), "username": username, "role_name": role_name},
            )
            raise UnexpectedDomainException(str(e)) from e
