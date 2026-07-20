from ips_app.config.seed_data import SEED_ROLES
from ips_app.domain.usecases.permission import PermissionUsecase
from ips_app.domain.usecases.role import RoleUsecase


async def seed_roles(
    permission_usecase: PermissionUsecase,
    role_usecase: RoleUsecase,
) -> None:
    for entry in SEED_ROLES:
        if await role_usecase.role_exists_by_name(entry["name"]):
            continue

        permission_ids = [
            (await permission_usecase.get_permission_by_name(name)).id
            for name in entry["permission_names"]
        ]

        role = await role_usecase.create_role(
            name=entry["name"],
            description=entry["description"],
            is_default=entry["is_default"],
        )

        if permission_ids:
            await role_usecase.add_permissions_to_role(role.id, permission_ids)
