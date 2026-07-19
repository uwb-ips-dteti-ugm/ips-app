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
    {
        "name": "node-network/manage",
        "description": "Create and update node networks",
    },
    {
        "name": "node-network/view",
        "description": "View node networks",
    },
    {
        "name": "node-network/delete",
        "description": "Delete node networks",
    },
    {
        "name": "node/manage",
        "description": "Create, update, and control nodes",
    },
    {
        "name": "node/view",
        "description": "View nodes",
    },
    {
        "name": "node/delete",
        "description": "Delete nodes",
    },
    {
        "name": "record/view",
        "description": "View positioning records",
    },
    {
        "name": "record/delete",
        "description": "Delete positioning records",
    },
]
