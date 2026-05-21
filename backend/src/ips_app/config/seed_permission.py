from typing import List, TypedDict


class PermissionSeed(TypedDict):
    name: str
    description: str


SEED_PERMISSIONS: List[PermissionSeed] = [
    {
        "name": "auth/manage",
        "description": "Manage user authentication settings",
    },
    {
        "name": "permission/manage",
        "description": "Create and update permissions",
    },
    {
        "name": "permission/view",
        "description": "View permissions",
    },
    {
        "name": "permission/delete",
        "description": "Delete permissions",
    },
    {
        "name": "role/manage",
        "description": "Create and update roles",
    },
    {
        "name": "role/view",
        "description": "View roles",
    },
    {
        "name": "role/delete",
        "description": "Delete roles",
    },
    {
        "name": "user/manage",
        "description": "Update users",
    },
    {
        "name": "user/view",
        "description": "View users",
    },
    {
        "name": "user/delete",
        "description": "Delete users",
    },
]
