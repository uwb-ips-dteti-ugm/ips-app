from typing import List

from ips_app.domain.models.seed import (
    AccountSeed,
    FeatureSeed,
    PermissionSeed,
    RoleSeed,
)


SEED_PERMISSIONS: List[PermissionSeed] = [
    {"name": "auth:manage", "description": "Manage authentication records"},
    {"name": "user:manage", "description": "Manage users"},
    {"name": "user:view", "description": "View users"},
    {"name": "user:delete", "description": "Delete users"},
    {"name": "role:manage", "description": "Manage roles"},
    {"name": "role:view", "description": "View roles"},
    {"name": "role:delete", "description": "Delete roles"},
    {"name": "permission:manage", "description": "Manage permissions"},
    {"name": "permission:view", "description": "View permissions"},
    {"name": "permission:delete", "description": "Delete permissions"},
    {"name": "feature:manage", "description": "Manage features"},
    {"name": "feature:view", "description": "View features"},
    {"name": "feature:delete", "description": "Delete features"},
]


SEED_FEATURES: List[FeatureSeed] = [
    {
        "name": "auth/manage",
        "description": "Access to authentication management",
        "permissions": ["auth:manage"],
    },
    {
        "name": "user/manage",
        "description": "Access to user management",
        "permissions": ["user:manage"],
    },
    {
        "name": "user/view",
        "description": "Access to view users",
        "permissions": ["user:view"],
    },
    {
        "name": "user/delete",
        "description": "Access to delete users",
        "permissions": ["user:delete"],
    },
    {
        "name": "role/manage",
        "description": "Access to role management",
        "permissions": ["role:manage"],
    },
    {
        "name": "role/view",
        "description": "Access to view roles",
        "permissions": ["role:view"],
    },
    {
        "name": "role/delete",
        "description": "Access to delete roles",
        "permissions": ["role:delete"],
    },
    {
        "name": "permission/manage",
        "description": "Access to permission management",
        "permissions": ["permission:manage"],
    },
    {
        "name": "permission/view",
        "description": "Access to view permissions",
        "permissions": ["permission:view"],
    },
    {
        "name": "permission/delete",
        "description": "Access to delete permissions",
        "permissions": ["permission:delete"],
    },
    {
        "name": "feature/manage",
        "description": "Access to feature management",
        "permissions": ["feature:manage"],
    },
    {
        "name": "feature/view",
        "description": "Access to view features",
        "permissions": ["feature:view"],
    },
    {
        "name": "feature/delete",
        "description": "Access to delete features",
        "permissions": ["feature:delete"],
    },
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
    {
        "name": "John Doe",
        "username": "johndoe",
        "password": "changeme",
        "role": "user",
    },
    {
        "name": "Jane Doe",
        "username": "janedoe",
        "password": "changeme",
        "role": "user",
    },
]
