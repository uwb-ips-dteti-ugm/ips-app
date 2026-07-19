from typing import Any

from beanie import PydanticObjectId


def to_object_id(value: Any) -> Any:
    if isinstance(value, str) and PydanticObjectId.is_valid(value):
        return PydanticObjectId(value)
    return value
