from typing import Dict, List

from ips_app.domain.usecases.role import RoleUsecase
from ips_app.domain.usecases.user import UserUsecase


async def seed_users(
    role_usecase: RoleUsecase,
    user_usecase: UserUsecase,
    entries: List[Dict[str, str]],
) -> None:
    for entry in entries:
        if await user_usecase.user_exists_by_username(entry["username"]):
            continue

        role = await role_usecase.get_role_by_name(entry["role_name"])
        await user_usecase.create_user(
            role_id=role.id,
            name=entry["name"],
            username=entry["username"],
            password=entry["password"],
        )
