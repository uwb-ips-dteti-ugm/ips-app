from typing import Any, Dict, List

SEED_PERMISSIONS: List[Dict[str, str]] = [
    {"name": "auth/manage", "description": "Manage authentication and user registration."},
    {"name": "permission/manage", "description": "Create and update permissions."},
    {"name": "permission/view", "description": "View permissions."},
    {"name": "permission/delete", "description": "Delete permissions."},
    {"name": "role/manage", "description": "Create and update roles."},
    {"name": "role/view", "description": "View roles."},
    {"name": "role/delete", "description": "Delete roles."},
    {"name": "user/manage", "description": "Create and update users."},
    {"name": "user/view", "description": "View users."},
    {"name": "user/delete", "description": "Delete users."},
    {"name": "node-network/manage", "description": "Create and update node networks."},
    {"name": "node-network/view", "description": "View node networks."},
    {"name": "node-network/delete", "description": "Delete node networks."},
    {"name": "node/manage", "description": "Create and update nodes."},
    {"name": "node/view", "description": "View nodes."},
    {"name": "node/delete", "description": "Delete nodes."},
    {"name": "ranging/manage", "description": "Report ranging measurements."},
    {"name": "ranging/view", "description": "View ranging records."},
    {"name": "ranging/delete", "description": "Delete ranging records."},
]

ADMIN_ROLE_NAME = "admin"
USER_ROLE_NAME = "user"

SEED_ROLES: List[Dict[str, Any]] = [
    {
        "name": ADMIN_ROLE_NAME,
        "description": "Full access to every resource.",
        "is_default": False,
        "permission_names": [permission["name"] for permission in SEED_PERMISSIONS],
    },
    {
        "name": USER_ROLE_NAME,
        "description": "Default role with no permissions.",
        "is_default": True,
        "permission_names": [],
    },
]


def build_seed_users(
    admin_name: str,
    admin_username: str,
    admin_password: str,
    user_name: str,
    user_username: str,
    user_password: str,
) -> List[Dict[str, str]]:
    return [
        {
            "role_name": ADMIN_ROLE_NAME,
            "name": admin_name,
            "username": admin_username,
            "password": admin_password,
        },
        {
            "role_name": USER_ROLE_NAME,
            "name": user_name,
            "username": user_username,
            "password": user_password,
        },
    ]
