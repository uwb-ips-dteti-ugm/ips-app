from ips_app.config.seed_user import UserSeed, build_seed_users
from ips_app.domain.ports.driving.seeder.user import UserSeeder


class UserSeederController:
    def __init__(
        self,
        service: UserSeeder,
        admin_name: str,
        admin_username: str,
        admin_password: str,
        user_name: str,
        user_username: str,
        user_password: str,
    ):
        self.service = service
        self.seeds: list[UserSeed] = build_seed_users(
            admin_name=admin_name,
            admin_username=admin_username,
            admin_password=admin_password,
            user_name=user_name,
            user_username=user_username,
            user_password=user_password,
        )

    async def seed(self) -> None:
        for seed in self.seeds:
            if await self.service.user_exists(seed["username"]):
                continue

            await self.service.add_user(
                name=seed["name"],
                username=seed["username"],
                password=seed["password"],
                role_name=seed["role_name"],
            )
