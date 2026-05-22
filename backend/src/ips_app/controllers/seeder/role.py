from ips_app.config.seed_role import SEED_ROLES, RoleSeed
from ips_app.domain.ports.driving.seeder.role import RoleSeeder


class RoleSeederController:
    def __init__(
        self,
        service: RoleSeeder,
        seeds: list[RoleSeed] = SEED_ROLES,
    ):
        self.service = service
        self.seeds = seeds

    async def seed(self) -> None:
        for seed in self.seeds:
            if await self.service.role_exists(seed["name"]):
                continue

            await self.service.add_role(
                name=seed["name"],
                description=seed["description"],
                is_default=seed["is_default"],
                permission_names=seed["permission_names"],
            )
