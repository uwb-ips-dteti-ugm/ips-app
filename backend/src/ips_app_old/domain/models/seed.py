from typing import List, TypedDict


class PermissionSeed(TypedDict):
    name: str
    description: str


class RoleSeed(TypedDict):
    name: str
    description: str
    is_default: bool
    permissions: List[str]


class FeatureSeed(TypedDict):
    name: str
    description: str
    permissions: List[str]
