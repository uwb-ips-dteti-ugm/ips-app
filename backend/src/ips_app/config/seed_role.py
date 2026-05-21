from typing import List, TypedDict

from ips_app.config.seed_permission import SEED_PERMISSIONS


class RoleSeed(TypedDict):
    name: str
    description: str
    is_default: bool
    permission_names: List[str]


ADMIN_ROLE_NAME = "admin"
USER_ROLE_NAME = "user"


SEED_ROLES: List[RoleSeed] = [
    {
        "name": ADMIN_ROLE_NAME,
        "description": "Administrator with full access",
        "is_default": False,
        "permission_names": [
            permission["name"]
            for permission in SEED_PERMISSIONS
        ],
    },
    {
        "name": USER_ROLE_NAME,
        "description": "Default user role",
        "is_default": True,
        "permission_names": [],
    },
]
