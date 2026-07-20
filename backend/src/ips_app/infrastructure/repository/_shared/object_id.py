from typing import Any, Optional, Type, TypeVar

from beanie import Document, PydanticObjectId


def to_object_id(value: Any) -> Any:
    if isinstance(value, str) and PydanticObjectId.is_valid(value):
        return PydanticObjectId(value)
    return value


TDocument = TypeVar("TDocument", bound=Document)


async def get_by_id(
    document_cls: Type[TDocument], id: Any, **kwargs: Any
) -> Optional[TDocument]:
    """Look up a document by its primary key, treating a malformed/non-ObjectId-shaped
    id as "not found" rather than letting it crash. `Document.get()` bypasses
    `to_object_id`'s lenient passthrough: it always coerces its argument via
    `parse_object_as(PydanticObjectId, ...)`, which raises a pydantic validation error
    (not a DomainException) for a value that isn't already a valid ObjectId shape.
    """
    if not (
        isinstance(id, PydanticObjectId)
        or (isinstance(id, str) and PydanticObjectId.is_valid(id))
    ):
        return None
    return await document_cls.get(id, **kwargs)
