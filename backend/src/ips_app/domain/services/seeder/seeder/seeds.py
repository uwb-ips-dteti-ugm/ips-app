from typing import List, TypedDict


class PermissionSeed(TypedDict):
    name: str
    description: str


class RoleSeed(TypedDict):
    name: str
    description: str
    is_default: bool
    permissions: List[str]


class AccountSeed(TypedDict):
    name: str
    username: str
    password: str
    role: str


SEED_PERMISSIONS: List[PermissionSeed] = [
    {"name": "auth:manage",       "description": "Manage authentication records"},
    {"name": "user:manage",       "description": "Manage users"},
    {"name": "user:view",         "description": "View users"},
    {"name": "user:delete",       "description": "Delete users"},
    {"name": "role:manage",       "description": "Manage roles"},
    {"name": "role:view",         "description": "View roles"},
    {"name": "role:delete",       "description": "Delete roles"},
    {"name": "permission:manage", "description": "Manage permissions"},
    {"name": "permission:view",   "description": "View permissions"},
    {"name": "permission:delete", "description": "Delete permissions"},
    {"name": "feature:manage",    "description": "Manage features"},
    {"name": "feature:view",      "description": "View features"},
    {"name": "feature:delete",    "description": "Delete features"},
]


ADMIN_ROLE_NAME = "admin"
SEED_ROLES: List[RoleSeed] = [
    {
        "name": ADMIN_ROLE_NAME,
        "description": "Administrator with full access",
        "is_default": False,
        "permissions": [
            "auth:manage",
            "user:manage",
            "user:view",
            "user:delete",
            "role:manage",
            "role:view",
            "role:delete",
            "permission:manage",
            "permission:view",
            "permission:delete",
            "feature:manage",
            "feature:view",
            "feature:delete",
        ],
    },
    {
        "name": "user",
        "description": "Default user with basic access",
        "is_default": True,
        "permissions": [],
    },
]

SEED_TEST_ACCOUNTS: List[AccountSeed] = [
    {"name": "John Doe", "username": "johndoe", "password": "changeme", "role": "user"},
    {"name": "Jane Doe", "username": "janedoe", "password": "changeme", "role": "user"},
]
