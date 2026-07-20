from ips_app.config.seed_data import SEED_PERMISSIONS
from ips_app.domain.usecases.permission import PermissionUsecase


async def seed_permissions(usecase: PermissionUsecase) -> None:
    for entry in SEED_PERMISSIONS:
        if await usecase.permission_exists_by_name(entry["name"]):
            continue
        await usecase.create_permission(
            name=entry["name"],
            description=entry["description"],
        )
