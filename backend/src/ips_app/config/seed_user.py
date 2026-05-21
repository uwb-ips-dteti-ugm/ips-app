from typing import List, TypedDict

from ips_app.config.seed_role import ADMIN_ROLE_NAME, USER_ROLE_NAME


class UserSeed(TypedDict):
    name: str
    username: str
    password: str
    role_name: str


def build_seed_users(
    admin_name: str,
    admin_username: str,
    admin_password: str,
    user_name: str,
    user_username: str,
    user_password: str,
) -> List[UserSeed]:
    return [
        {
            "name": admin_name,
            "username": admin_username,
            "password": admin_password,
            "role_name": ADMIN_ROLE_NAME,
        },
        {
            "name": user_name,
            "username": user_username,
            "password": user_password,
            "role_name": USER_ROLE_NAME,
        },
    ]
