from ips_app.config.seed_permission import SEED_PERMISSIONS, PermissionSeed
from ips_app.domain.ports.driving.seeder.permission import PermissionSeeder


class PermissionSeederController:
    def __init__(
        self,
        service: PermissionSeeder,
        seeds: list[PermissionSeed] = SEED_PERMISSIONS,
    ):
        self.service = service
        self.seeds = seeds

    async def seed(self) -> None:
        for seed in self.seeds:
            if await self.service.permission_exists(seed["name"]):
                continue

            await self.service.add_permission(
                name=seed["name"],
                description=seed["description"],
            )
